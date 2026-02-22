import { useEffect, useState } from "react";
import API from "../services/api";

function Orders() {
  const [orders, setOrders] = useState([]);

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      const response = await API.get("/orders/");
      setOrders(response.data);
    } catch (error) {
      console.error("Error fetching orders", error);
    }
  };

  return (
    <div>
      <h2>My Orders</h2>

      {orders.length === 0 && <p>No orders yet</p>}

      {orders.map((order) => (
        <div
          key={order.order_id}
          style={{
            border: "1px solid black",
            margin: "10px",
            padding: "10px",
          }}
        >
          <h3>Order ID: {order.order_id}</h3>
          <p>Total Amount: ₹{order.total_amount}</p>
          <p>Status: {order.status}</p>
          <p>Date: {new Date(order.created_at).toLocaleString()}</p>
        </div>
      ))}
    </div>
  );
}

export default Orders;