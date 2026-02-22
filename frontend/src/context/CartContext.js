import { createContext, useContext, useEffect, useState } from "react";
import API from "../services/api";
import { useAuth } from "./AuthContext";

const CartContext = createContext();

export function CartProvider({ children }) {
  const { token } = useAuth();
  const [cartItems, setCartItems] = useState([]);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    if (token) {
      fetchCart();
    } else {
      setCartItems([]);
      setTotal(0);
    }
  }, [token]);

  const fetchCart = async () => {
    try {
      const res = await API.get("/cart/");
      setCartItems(res.data.cart_items);
      setTotal(res.data.total_price);
    } catch (error) {
      console.error("Cart fetch failed");
    }
  };

  const addToCart = async (productId) => {
    await API.post("/cart/add", {
      product_id: productId,
      quantity: 1,
    });
    fetchCart();
  };

  const removeFromCart = async (productId) => {
    await API.delete(`/cart/remove/${productId}`);
    fetchCart();
  };

  const updateQuantity = async (productId, quantity) => {
    await API.put("/cart/update", {
      product_id: productId,
      quantity: quantity,
    });
    fetchCart();
  };

  return (
    <CartContext.Provider
      value={{
        cartItems,
        total,
        fetchCart,
        addToCart,
        removeFromCart,
        updateQuantity,
      }}
    >
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  return useContext(CartContext);
}