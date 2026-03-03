import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, FlatList, Image } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { useAuthStore } from '../../store/authStore';

const RESTAURANTS = [
  { id: '1', name: 'Burger King', cuisine: 'Fast Food', rating: 4.5, deliveryTime: '30-45 min', image: 'https://via.placeholder.com/100' },
  { id: '2', name: 'Pizza Hut', cuisine: 'Italian', rating: 4.3, deliveryTime: '25-40 min', image: 'https://via.placeholder.com/100' },
  { id: '3', name: 'Sushi Place', cuisine: 'Japanese', rating: 4.7, deliveryTime: '35-50 min', image: 'https://via.placeholder.com/100' },
];

export const HomeScreen: React.FC = () => {
  const navigation = useNavigation();
  const { user, logout } = useAuthStore();

  const handleLogout = async () => {
    await logout();
  };

  const renderRestaurant = ({ item }: { item: typeof RESTAURANTS[0] }) => (
    <TouchableOpacity style={styles.restaurantCard}>
      <Image source={{ uri: item.image }} style={styles.restaurantImage} />
      <View style={styles.restaurantInfo}>
        <Text style={styles.restaurantName}>{item.name}</Text>
        <Text style={styles.cuisine}>{item.cuisine}</Text>
        <View style={styles.metaRow}>
          <Text style={styles.rating}>⭐ {item.rating}</Text>
          <Text style={styles.deliveryTime}>🕐 {item.deliveryTime}</Text>
        </View>
      </View>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.greeting}>Hello, {user?.full_name || 'Guest'} 👋</Text>
        <Text style={styles.subtitle}>What would you like to order?</Text>
      </View>

      <FlatList
        data={RESTAURANTS}
        renderItem={renderRestaurant}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.list}
        showsVerticalScrollIndicator={false}
      />

      <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
        <Text style={styles.logoutText}>Logout</Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    padding: 20,
    backgroundColor: '#FF6B6B',
  },
  greeting: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
  },
  subtitle: {
    fontSize: 16,
    color: '#fff',
    marginTop: 5,
  },
  list: {
    padding: 15,
  },
  restaurantCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    marginBottom: 15,
    flexDirection: 'row',
    padding: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  restaurantImage: {
    width: 80,
    height: 80,
    borderRadius: 8,
  },
  restaurantInfo: {
    flex: 1,
    marginLeft: 15,
    justifyContent: 'center',
  },
  restaurantName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  cuisine: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  metaRow: {
    flexDirection: 'row',
    marginTop: 8,
  },
  rating: {
    fontSize: 14,
    color: '#666',
    marginRight: 15,
  },
  deliveryTime: {
    fontSize: 14,
    color: '#666',
  },
  logoutButton: {
    backgroundColor: '#ff4444',
    margin: 20,
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
  },
  logoutText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
