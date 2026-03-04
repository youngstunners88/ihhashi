"""
Nduna Route Memory Integration - Phase 4

Integrates route memory with Nduna chatbot for:
- ETAs using route memory
- Best route suggestions
- Community insight alerts
- Driver performance analytics
"""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from bson import ObjectId
import math
import json

from app.database import get_collection
from app.models.route_memory import (
    RouteIntelligence, InsightType, Weather
)
from app.models.community import (
    ValidationStatus, ReputationLevel
)

router = APIRouter(prefix="/nduna-intelligence", tags=["nduna-integration"])


# ============================================================================
# COLLECTION HELPERS
# ============================================================================

def segments_collection():
    return get_collection("route_segments")

def insights_collection():
    return get_collection("driver_insights")

def time_records_collection():
    return get_collection("actual_time_records")

def feedback_collection():
    return get_collection("route_feedback")

def validations_collection():
    return get_collection("insight_validations")

def reputations_collection():
    return get_collection("driver_reputations")

def knowledge_points_collection():
    return get_collection("knowledge_points")

def orders_collection():
    return get_collection("orders")


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate distance between two points in meters"""
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


def get_time_of_day_factor(hour: int) -> float:
    """Get time adjustment factor based on hour"""
    # Peak hours: 7-9, 16-18
    if 7 <= hour <= 9 or 16 <= hour <= 18:
        return 1.5
    # Late night: 22-6
    elif 22 <= hour or hour <= 6:
        return 0.8
    return 1.0


def get_day_of_week_factor(day: int) -> float:
    """Get day adjustment factor (0=Monday)"""
    # Weekend is faster
    if day in [5, 6]:  # Saturday, Sunday
        return 0.85
    return 1.0


# ============================================================================
# ETA CALCULATION WITH ROUTE MEMORY
# ============================================================================

@router.get("/eta")
async def calculate_eta(
    from_lat: float,
    from_lng: float,
    to_lat: float,
    to_lng: float,
    driver_id: Optional[str] = None
):
    """
    Calculate ETA using route memory data.
    
    Returns:
    - Base ETA (distance-based)
    - Adjusted ETA (with time factors)
    - Confidence level
    - Active alerts
    """
    # Calculate base distance and time
    distance_m = haversine_distance(from_lat, from_lng, to_lat, to_lng)
    
    # Base time: 30 km/h average = 2 min/km
    base_time_seconds = (distance_m / 1000) * 120
    
    # Get current time factors
    now = datetime.utcnow()
    time_factor = get_time_of_day_factor(now.hour)
    day_factor = get_day_of_week_factor(now.weekday())
    
    # Try to get segment-specific data
    segments = segments_collection()
    
    # Find segments near start and end
    nearby_start = await segments.find({
        "start_point.lat": {"$gte": from_lat - 0.005, "$lte": from_lat + 0.005},
        "start_point.lng": {"$gte": from_lng - 0.005, "$lte": from_lng + 0.005}
    }).to_list(length=10)
    
    nearby_end = await segments.find({
        "end_point.lat": {"$gte": to_lat - 0.005, "$lte": to_lat + 0.005},
        "end_point.lng": {"$gte": to_lng - 0.005, "$lte": to_lng + 0.005}
    }).to_list(length=10)
    
    # Calculate segment-specific factors
    segment_factor = 1.0
    confidence = 0.5  # Base confidence
    
    if nearby_start or nearby_end:
        # We have some segment data
        all_nearby = nearby_start + nearby_end
        
        # Average time factors from segments
        avg_peak = sum(s.get("time_factors", {}).get("peak_hour_factor", 1.0) for s in all_nearby) / len(all_nearby)
        avg_weekend = sum(s.get("time_factors", {}).get("weekend_factor", 1.0) for s in all_nearby) / len(all_nearby)
        
        # Apply segment-specific factors
        if time_factor > 1.0:  # Peak hour
            segment_factor = avg_peak
        elif now.weekday() in [5, 6]:  # Weekend
            segment_factor = avg_weekend
        
        # Increase confidence based on segment data
        total_confidence_points = sum(s.get("confidence", 0) for s in all_nearby)
        confidence = min(0.5 + (total_confidence_points / 100), 0.95)
    
    # Apply driver-specific accuracy if available
    if driver_id:
        time_records = time_records_collection()
        
        # Get driver's recent accuracy
        cutoff = datetime.utcnow() - timedelta(days=30)
        pipeline = [
            {"$match": {"driver_id": driver_id, "created_at": {"$gte": cutoff}}},
            {"$group": {
                "_id": None,
                "avg_accuracy": {"$avg": {
                    "$cond": [
                        {"$gt": ["$expected_time_seconds", 0]},
                        {"$min": [
                            {"$abs": {"$subtract": ["$actual_time_seconds", "$expected_time_seconds"]}},
                            "$expected_time_seconds"
                        ]},
                        0
                    ]
                }}
            }}
        ]
        
        driver_stats = await time_records.aggregate(pipeline).to_list(length=1)
        if driver_stats and driver_stats[0].get("avg_accuracy") is not None:
            # Adjust confidence based on driver accuracy
            driver_accuracy = 1 - (driver_stats[0]["avg_accuracy"] / 100)
            confidence = (confidence + driver_accuracy) / 2
    
    # Calculate final ETA
    adjusted_time = base_time_seconds * time_factor * day_factor * segment_factor
    
    # Get active alerts
    alerts = await get_route_alerts(from_lat, from_lng, to_lat, to_lng)
    
    # Add alert delays
    alert_delay = sum(a.get("delay_minutes", 0) * 60 for a in alerts)
    adjusted_time += alert_delay
    
    return {
        "distance_m": int(distance_m),
        "distance_km": round(distance_m / 1000, 2),
        "base_eta_seconds": int(base_time_seconds),
        "base_eta_minutes": round(base_time_seconds / 60, 1),
        "adjusted_eta_seconds": int(adjusted_time),
        "adjusted_eta_minutes": round(adjusted_time / 60, 1),
        "confidence": round(confidence, 2),
        "confidence_level": "high" if confidence >= 0.8 else "medium" if confidence >= 0.6 else "low",
        "factors_applied": {
            "time_of_day": time_factor,
            "day_of_week": day_factor,
            "segment": segment_factor
        },
        "active_alerts": alerts,
        "alert_count": len(alerts)
    }


# ============================================================================
# ROUTE SUGGESTIONS
# ============================================================================

@router.get("/suggest-route")
async def suggest_best_route(
    from_lat: float,
    from_lng: float,
    to_lat: float,
    to_lng: float
):
    """
    Suggest best route based on community knowledge.
    
    Returns:
    - Primary route with ETA
    - Alternative routes if available
    - Community tips
    - Areas to avoid
    """
    # Get ETA for primary route
    primary_eta = await calculate_eta(from_lat, from_lng, to_lat, to_lng)
    
    # Get knowledge points along route
    knowledge = knowledge_points_collection()
    
    # Simple route corridor check (would use proper routing in production)
    corridor_points = await knowledge.find({
        "validation_status": ValidationStatus.CONFIRMED.value,
        "$or": [
            {"location.lat": {"$gte": min(from_lat, to_lat) - 0.01, "$lte": max(from_lat, to_lat) + 0.01}},
            {"location.lng": {"$gte": min(from_lng, to_lng) - 0.01, "$lte": max(from_lng, to_lng) + 0.01}}
        ]
    }).to_list(length=50)
    
    # Categorize knowledge
    shortcuts = []
    avoid_areas = []
    tips = []
    
    for point in corridor_points:
        category = point.get("category", "")
        
        if category == "shortcut":
            shortcuts.append({
                "location": point.get("location"),
                "insight_count": point.get("insight_count", 0),
                "helpfulness_ratio": point.get("helpfulness_ratio", 0)
            })
        elif category in ["avoid_zone", "safety"]:
            avoid_areas.append({
                "location": point.get("location"),
                "reason": category,
                "insight_count": point.get("insight_count", 0)
            })
        elif category in ["delivery_tip", "access_point"]:
            tips.append({
                "location": point.get("location"),
                "category": category,
                "insight_count": point.get("insight_count", 0)
            })
    
    # Get validated insights along route
    insights = insights_collection()
    validations = validations_collection()
    
    validated_insights = []
    async for insight in insights.find({
        "location.lat": {"$gte": min(from_lat, to_lat) - 0.01, "$lte": max(from_lat, to_lat) + 0.01}
    }):
        validation = await validations.find_one({"insight_id": str(insight["_id"])})
        if validation and validation.get("status") == ValidationStatus.CONFIRMED.value:
            validated_insights.append({
                "type": insight.get("type"),
                "description": insight.get("description"),
                "location": insight.get("location"),
                "saves_minutes": insight.get("saves_minutes")
            })
    
    return {
        "primary_route": {
            "eta_seconds": primary_eta["adjusted_eta_seconds"],
            "eta_minutes": primary_eta["adjusted_eta_minutes"],
            "confidence": primary_eta["confidence"],
            "distance_m": primary_eta["distance_m"]
        },
        "shortcuts": shortcuts[:5],
        "avoid_areas": avoid_areas[:5],
        "tips": tips[:5],
        "validated_insights": validated_insights[:10],
        "recommendations": generate_route_recommendations(shortcuts, avoid_areas, validated_insights)
    }


def generate_route_recommendations(shortcuts: list, avoid_areas: list, insights: list) -> list:
    """Generate route recommendations"""
    recommendations = []
    
    if shortcuts:
        best_shortcut = max(shortcuts, key=lambda x: x.get("helpfulness_ratio", 0))
        recommendations.append(f"Consider shortcut near {best_shortcut['location']} - highly rated by drivers")
    
    if avoid_areas:
        recommendations.append(f"Avoid {len(avoid_areas)} marked areas along this route")
    
    time_saving_insights = [i for i in insights if i.get("saves_minutes", 0) > 0]
    if time_saving_insights:
        total_saved = sum(i.get("saves_minutes", 0) for i in time_saving_insights)
        recommendations.append(f"Community tips can save ~{total_saved} minutes on this route")
    
    return recommendations


# ============================================================================
# ALERTS
# ============================================================================

async def get_route_alerts(
    from_lat: float,
    from_lng: float,
    to_lat: float,
    to_lng: float
) -> list:
    """Get active alerts for a route"""
    insights = insights_collection()
    
    # Find recent, active alerts
    now = datetime.utcnow()
    cutoff = now - timedelta(hours=24)
    
    alerts = []
    
    async for insight in insights.find({
        "type": {"$in": ["road_work", "unsafe", "avoid"]},
        "created_at": {"$gte": cutoff},
        "$or": [
            {"expires_at": None},
            {"expires_at": {"$gt": now}}
        ],
        "location.lat": {"$gte": min(from_lat, to_lat) - 0.02, "$lte": max(from_lat, to_lat) + 0.02},
        "location.lng": {"$gte": min(from_lng, to_lng) - 0.02, "$lte": max(from_lng, to_lng) + 0.02}
    }):
        delay_minutes = 5 if insight.get("type") == "road_work" else 0
        
        alerts.append({
            "type": insight.get("type"),
            "description": insight.get("description"),
            "location": insight.get("location"),
            "delay_minutes": delay_minutes,
            "expires_at": insight.get("expires_at")
        })
    
    return alerts


@router.get("/alerts/nearby")
async def get_nearby_alerts(
    lat: float,
    lng: float,
    radius_m: float = Query(default=2000)
):
    """Get alerts near a location"""
    insights = insights_collection()
    
    now = datetime.utcnow()
    
    # Convert radius to degrees (rough approximation)
    radius_deg = radius_m / 111000  # ~111km per degree
    
    alerts = []
    
    async for insight in insights.find({
        "type": {"$in": ["road_work", "unsafe", "avoid", "slow_zone"]},
        "location.lat": {"$gte": lat - radius_deg, "$lte": lat + radius_deg},
        "location.lng": {"$gte": lng - radius_deg, "$lte": lng + radius_deg},
        "$or": [
            {"expires_at": None},
            {"expires_at": {"$gt": now}}
        ]
    }):
        alerts.append({
            "type": insight.get("type"),
            "description": insight.get("description"),
            "location": insight.get("location"),
            "driver_id": insight.get("driver_id"),
            "created_at": insight.get("created_at")
        })
    
    return {
        "alerts": alerts,
        "count": len(alerts),
        "center": {"lat": lat, "lng": lng},
        "radius_m": radius_m
    }


# ============================================================================
# DRIVER PERFORMANCE ANALYTICS
# ============================================================================

@router.get("/driver/{driver_id}/performance")
async def get_driver_performance(
    driver_id: str,
    days: int = Query(default=30, ge=1, le=90)
):
    """Get driver performance analytics"""
    time_records = time_records_collection()
    feedback = feedback_collection()
    reputations = reputations_collection()
    
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    # Get time records
    records = await time_records.find({
        "driver_id": driver_id,
        "created_at": {"$gte": cutoff}
    }).to_list(length=1000)
    
    # Calculate metrics
    total_deliveries = len(records)
    
    if total_deliveries > 0:
        avg_expected = sum(r.get("expected_time_seconds", 0) for r in records) / total_deliveries
        avg_actual = sum(r.get("actual_time_seconds", 0) for r in records) / total_deliveries
        
        # Accuracy: how close actual is to expected
        accuracies = []
        for r in records:
            exp = r.get("expected_time_seconds", 0)
            act = r.get("actual_time_seconds", 0)
            if exp > 0:
                accuracy = 1 - min(abs(act - exp) / exp, 1)
                accuracies.append(accuracy)
        
        avg_accuracy = sum(accuracies) / len(accuracies) if accuracies else 0
    else:
        avg_expected = 0
        avg_actual = 0
        avg_accuracy = 0
    
    # Get feedback stats
    feedback_records = await feedback.find({
        "driver_id": driver_id,
        "created_at": {"$gte": cutoff}
    }).to_list(length=500)
    
    smooth_count = sum(1 for f in feedback_records if f.get("feedback_type") == "smooth")
    delayed_count = sum(1 for f in feedback_records if f.get("feedback_type") == "delayed")
    
    # Get reputation
    reputation = await reputations.find_one({"driver_id": driver_id})
    
    # Performance trends (by week)
    weekly_stats = []
    for i in range(min(days // 7, 4)):
        week_start = datetime.utcnow() - timedelta(weeks=i+1)
        week_end = datetime.utcnow() - timedelta(weeks=i)
        
        week_records = [r for r in records 
                       if week_start <= r.get("created_at", datetime.utcnow()) <= week_end]
        
        if week_records:
            week_accuracy = sum(
                1 - min(abs(r.get("actual_time_seconds", 0) - r.get("expected_time_seconds", 1)) / 
                       max(r.get("expected_time_seconds", 1), 1), 1)
                for r in week_records
            ) / len(week_records)
        else:
            week_accuracy = 0
        
        weekly_stats.append({
            "week": i + 1,
            "deliveries": len(week_records),
            "accuracy": round(week_accuracy, 2)
        })
    
    return {
        "driver_id": driver_id,
        "period_days": days,
        "total_deliveries": total_deliveries,
        "avg_expected_seconds": round(avg_expected, 1),
        "avg_actual_seconds": round(avg_actual, 1),
        "prediction_accuracy": round(avg_accuracy, 2),
        "accuracy_rating": "excellent" if avg_accuracy >= 0.9 else "good" if avg_accuracy >= 0.75 else "average" if avg_accuracy >= 0.6 else "needs_improvement",
        "feedback": {
            "smooth": smooth_count,
            "delayed": delayed_count,
            "smooth_rate": round(smooth_count / len(feedback_records) * 100, 1) if feedback_records else 0
        },
        "reputation": {
            "level": reputation.get("level", "newcomer") if reputation else "newcomer",
            "points": reputation.get("total_points", 0) if reputation else 0,
            "badges": reputation.get("badges", []) if reputation else []
        } if reputation else None,
        "weekly_trend": weekly_stats
    }


# ============================================================================
# NDUNA CONTEXT PROVIDER
# ============================================================================

@router.get("/context")
async def get_nduna_context(
    customer_lat: Optional[float] = None,
    customer_lng: Optional[float] = None,
    merchant_lat: Optional[float] = None,
    merchant_lng: Optional[float] = None,
    driver_id: Optional[str] = None
):
    """
    Get context for Nduna chatbot.
    
    Returns all relevant information in a format Nduna can use.
    """
    context = {
        "timestamp": datetime.utcnow().isoformat(),
        "route_intelligence": None,
        "driver_performance": None,
        "alerts": []
    }
    
    # Get route intelligence if we have coordinates
    if customer_lat and customer_lng and merchant_lat and merchant_lng:
        eta = await calculate_eta(merchant_lat, merchant_lng, customer_lat, customer_lng)
        suggestions = await suggest_best_route(merchant_lat, merchant_lng, customer_lat, customer_lng)
        
        context["route_intelligence"] = {
            "eta_minutes": eta["adjusted_eta_minutes"],
            "confidence": eta["confidence"],
            "distance_km": eta["distance_km"],
            "alerts": eta["active_alerts"],
            "recommendations": suggestions["recommendations"]
        }
        
        # Get nearby alerts
        if customer_lat and customer_lng:
            alerts = await get_nearby_alerts(customer_lat, customer_lng, 2000)
            context["alerts"] = alerts["alerts"]
    
    # Get driver performance if driver_id provided
    if driver_id:
        performance = await get_driver_performance(driver_id, 30)
        context["driver_performance"] = {
            "accuracy": performance["prediction_accuracy"],
            "level": performance.get("reputation", {}).get("level", "newcomer"),
            "recent_deliveries": performance["total_deliveries"]
        }
    
    return context


# ============================================================================
# ANALYTICS DASHBOARD DATA
# ============================================================================

@router.get("/dashboard")
async def get_intelligence_dashboard():
    """Get data for performance analytics dashboard"""
    
    # Total insights
    total_insights = await insights_collection().count_documents({})
    validated_insights = await validations_collection().count_documents({
        "status": ValidationStatus.CONFIRMED.value
    })
    
    # Active drivers with reputation
    active_drivers = await reputations_collection().count_documents({
        "total_points": {"$gt": 0}
    })
    
    # Knowledge points
    total_knowledge = await knowledge_points_collection().count_documents({})
    
    # Recent activity (last 7 days)
    cutoff = datetime.utcnow() - timedelta(days=7)
    
    recent_time_records = await time_records_collection().count_documents({
        "created_at": {"$gte": cutoff}
    })
    
    recent_insights = await insights_collection().count_documents({
        "created_at": {"$gte": cutoff}
    })
    
    recent_feedback = await feedback_collection().count_documents({
        "created_at": {"$gte": cutoff}
    })
    
    # Top contributors
    top_drivers = await reputations_collection().find().sort("total_points", -1).limit(5).to_list(length=5)
    
    for driver in top_drivers:
        driver["id"] = str(driver["_id"])
        del driver["_id"]
    
    return {
        "overview": {
            "total_insights": total_insights,
            "validated_insights": validated_insights,
            "validation_rate": round(validated_insights / total_insights * 100, 1) if total_insights > 0 else 0,
            "active_drivers": active_drivers,
            "knowledge_points": total_knowledge
        },
        "recent_activity": {
            "time_records_7d": recent_time_records,
            "new_insights_7d": recent_insights,
            "feedback_7d": recent_feedback
        },
        "top_contributors": top_drivers,
        "system_health": {
            "status": "healthy",
            "last_updated": datetime.utcnow().isoformat()
        }
    }


# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get("/health")
async def health_check():
    """Check Nduna integration status"""
    segments_count = await segments_collection().count_documents({})
    insights_count = await insights_collection().count_documents({})
    time_records_count = await time_records_collection().count_documents({})
    
    return {
        "status": "healthy",
        "collections": {
            "route_segments": segments_count,
            "driver_insights": insights_count,
            "time_records": time_records_count
        },
        "features": {
            "eta_calculation": "active",
            "route_suggestions": "active",
            "alerts": "active",
            "driver_analytics": "active"
        }
    }
