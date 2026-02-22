import { useEffect, useState } from "react";
import API from "../services/api";

function AdminProducts() {
  const [products, setProducts] = useState([]);
  const [form, setForm] = useState({
    name: "",
    description: "",
    price: "",
    image_url: "",
    category: "",
    stock: "",
  });

  const [editingId, setEditingId] = useState(null);

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    const res = await API.get("/products/");
    setProducts(res.data);
  };

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      if (editingId) {
        await API.put(`/products/${editingId}`, form);
        alert("Product updated");
      } else {
        await API.post("/products/", form);
        alert("Product added");
      }

      setForm({
        name: "",
        description: "",
        price: "",
        image_url: "",
        category: "",
        stock: "",
      });

      setEditingId(null);
      fetchProducts();
    } catch (err) {
      alert("Admin access required");
    }
  };

  const handleEdit = (product) => {
    setForm(product);
    setEditingId(product.id);
  };

  const handleDelete = async (id) => {
    try {
      await API.delete(`/products/${id}`);
      alert("Deleted");
      fetchProducts();
    } catch {
      alert("Admin access required");
    }
  };

  return (
    <div className="container mt-4">
      <h2>Admin Products</h2>

      <form onSubmit={handleSubmit} className="mb-4">
        <input name="name" placeholder="Name" value={form.name} onChange={handleChange} required />
        <input name="description" placeholder="Description" value={form.description} onChange={handleChange} required />
        <input name="price" placeholder="Price" value={form.price} onChange={handleChange} required />
        <input name="image_url" placeholder="Image URL" value={form.image_url} onChange={handleChange} required />
        <input name="category" placeholder="Category" value={form.category} onChange={handleChange} required />
        <input name="stock" placeholder="Stock" value={form.stock} onChange={handleChange} required />

        <button type="submit" className="btn btn-primary">
          {editingId ? "Update" : "Add"} Product
        </button>
      </form>

      {products.map((p) => (
        <div key={p.id} className="border p-2 mb-2">
          <h5>{p.name}</h5>
          <button className="btn btn-warning me-2" onClick={() => handleEdit(p)}>Edit</button>
          <button className="btn btn-danger" onClick={() => handleDelete(p.id)}>Delete</button>
        </div>
      ))}
    </div>
  );
}

export default AdminProducts;