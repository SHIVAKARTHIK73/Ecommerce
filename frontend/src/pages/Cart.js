import { useEffect, useState } from "react";
import API from "../services/api";

function Cart() {
  const [cart, setCart] = useState([]);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    fetchCart();
  }, []);

  const fetchCart = async () => {
    try {
      const response = await API.get("/cart/");
      setCart(response.data.cart_items);
      setTotal(response.data.total_price);
    } catch (error) {
      console.error("Error fetching cart", error);
    }
  };

  const placeOrder = async () => {
    try {
      const response = await API.post("/orders/");
      alert("Order placed successfully");
      fetchCart(); // refresh cart
    } catch (error) {
      alert("Cart is empty or login required");
    }
  };

  return (
    <div>
      <h2>Cart</h2>

      {cart.length === 0 && <p>No items in cart</p>}

      {cart.map((item, index) => (
        <div key={index} style={{ border: "1px solid black", margin: "10px", padding: "10px" }}>
          <h3>{item.name}</h3>
          <p>Price: ₹{item.price}</p>
          <p>Quantity: {item.quantity}</p>
          <p>Item Total: ₹{item.item_total}</p>
        </div>
      ))}

      <h3>Total: ₹{total}</h3>

      {cart.length > 0 && (
        <button onClick={placeOrder}>Place Order</button>
      )}
    </div>
  );
}

export default Cart;