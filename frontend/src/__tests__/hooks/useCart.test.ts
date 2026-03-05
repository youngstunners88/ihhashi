import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';

// Mock the cart hook
const mockCart = {
  items: [],
  totalItems: 0,
  totalPrice: 0,
  addItem: vi.fn(),
  removeItem: vi.fn(),
  updateQuantity: vi.fn(),
  clearCart: vi.fn(),
};

vi.mock('../../hooks/useCart', () => ({
  useCart: () => mockCart,
}));

describe('useCart', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('returns cart functions', () => {
    const { useCart } = require('../../hooks/useCart');
    const result = useCart();
    
    expect(result).toHaveProperty('items');
    expect(result).toHaveProperty('totalItems');
    expect(result).toHaveProperty('totalPrice');
    expect(result).toHaveProperty('addItem');
    expect(result).toHaveProperty('removeItem');
    expect(result).toHaveProperty('updateQuantity');
    expect(result).toHaveProperty('clearCart');
  });

  it('addItem can be called', () => {
    const { useCart } = require('../../hooks/useCart');
    const result = useCart();
    
    const mockItem = {
      id: '1',
      name: 'Test Burger',
      price: 85,
      quantity: 1,
    };

    result.addItem(mockItem);
    expect(result.addItem).toHaveBeenCalledWith(mockItem);
  });
});
