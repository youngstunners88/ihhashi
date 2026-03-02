# Nduna Bot - Future Features Roadmap

> Last updated: 2026-02-19
> Current version: 0.5.0

## High Priority

### 1. Order Placement via Chat
**Status**: Planned
**Priority**: High
**Estimated effort**: 2-3 weeks

**Description**:
Enable Nduna to place orders directly through natural language conversation.

**Example commands**:
- "Get me a coke and a chicken burger from Thembis Chicken"
- "Order 2x milk and bread from the closest supermarket"
- "I want a large pepperoni pizza from Pizza Place"

**Requirements**:
- [ ] Natural language item parsing (extract items, quantities, modifiers)
- [ ] Merchant matching and verification
- [ ] Product availability checking
- [ ] Cart management (add/update/remove items)
- [ ] Checkout flow integration
- [ ] Payment gateway integration (PayStack/Yoco)
- [ ] Order confirmation and tracking
- [ ] Error handling (out of stock, closed, etc.)

**Technical approach**:
1. Add function calling tools: `add_to_cart`, `remove_from_cart`, `checkout`, `get_order_status`
2. Integrate with existing iHhashi order API
3. Add payment confirmation flow
4. Support both registered and guest users

**Dependencies**:
- Payment gateway setup
- Order API endpoints ready
- User authentication flow

---

### 2. South African Male Voice (TTS)
**Status**: Planned
**Priority**: Medium
**Estimated effort**: 1 week

**Description**:
Give Nduna a male South African voice for text-to-speech responses.

**Requirements**:
- [ ] Select TTS provider with SA accent support
- [ ] Configure male voice profile
- [ ] Integrate with Nduna response flow
- [ ] Add voice response endpoint
- [ ] Support WhatsApp voice notes

**Provider options**:

| Provider | SA Accent | Custom Voice | Cost |
|----------|-----------|--------------|------|
| ElevenLabs | Yes (can clone) | Yes | $$$ |
| Google TTS | Limited | No | $ |
| Azure TTS | Limited | Yes | $$ |
| Amazon Polly | No | No | $ |

**Recommended**: ElevenLabs
- Can clone a real SA male voice
- High quality natural speech
- API integration available
- Custom voice creation (~$5/month)

**Technical approach**:
1. Record or source SA male voice samples
2. Train custom voice on ElevenLabs
3. Add `/nduna/voice-response` endpoint
4. Return audio file with response
5. WhatsApp: send as voice note

---

## Medium Priority

### 3. Multi-language Voice Support
**Status**: Planned
**Priority**: Medium

Support voice input/output in all 11 SA languages:
- Zulu, Xhosa, Afrikaans, English
- Sepedi, Setswana, Sesotho
- Tsonga, Swati, Venda, Ndebele

### 4. Order History & Reordering
**Status**: Planned
**Priority**: Medium

- "Order the same as last time"
- "What did I order from [merchant] before?"
- Quick reorder buttons

### 5. Smart Suggestions
**Status**: Planned
**Priority**: Medium

Context-aware suggestions based on:
- Time of day (breakfast, lunch, dinner)
- Weather (cold drinks on hot days)
- Past orders
- Location

---

## Low Priority / Ideas

### 6. Group Ordering
Multiple people can add to same order via shared link

### 7. Subscription Orders
"Every Monday morning, order me a coffee from [place]"

### 8. Voice Ordering Flow
Full voice-first ordering experience:
1. User speaks order
2. Nduna confirms via voice
3. User confirms via voice
4. Payment via saved method
5. Status updates via voice notes

---

## Completed Features

| Feature | Version | Date |
|---------|---------|------|
| Basic chat with LLM | 0.1.0 | 2026-01 |
| WhatsApp integration | 0.2.0 | 2026-01 |
| Multi-language support (7 languages) | 0.3.0 | 2026-02 |
| Product browsing with function calling | 0.5.0 | 2026-02-19 |
| Voice input (STT) | 0.5.0 | 2026-02-19 |

---

## Notes

- Keep user experience simple - natural language should feel natural
- Voice features should complement text, not replace
- Payment integration is critical for order placement
- Consider data costs for voice features in SA market
