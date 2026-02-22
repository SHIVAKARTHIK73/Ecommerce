import { useEffect, useState } from "react";
import API from "../services/api";

function Products() {
  const [products, setProducts] = useState([]);

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      const response = await API.get("/products/");
      setProducts(response.data);
    } catch (error) {
      console.error("Error fetching products", error);
    }
  };

  const addToCart = async (productId) => {
    try {
      await API.post("/cart/add", {
        product_id: productId,
        quantity: 1,
      });
      alert("Added to cart");
    } catch (error) {
      alert("Login required to add to cart");
    }
  };

  return (
    <div>
      <h2>Products</h2>

      {products.map((product) => (
        <div key={product.id} style={{ border: "1px solid black", margin: "10px", padding: "10px" }}>
          <h3>{product.name}</h3>
          <p>{product.description}</p>
          <p>Price: ₹{product.price}</p>
          <button onClick={() => addToCart(product.id)}>
            Add to Cart
          </button>
        </div>
      ))}
    </div>
  );
}

export default Products;