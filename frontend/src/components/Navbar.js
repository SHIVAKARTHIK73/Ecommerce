import { Link, useNavigate } from "react-router-dom";

function Navbar() {
  const navigate = useNavigate();
  const token = localStorage.getItem("token");

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-dark px-4">
      <Link className="navbar-brand" to="/">Ecommerce</Link>

      <div className="ms-auto">
        <Link className="btn btn-outline-light me-2" to="/">Products</Link>
        {token && <Link className="btn btn-outline-light me-2" to="/cart">Cart</Link>}
        {token && <Link className="btn btn-outline-light me-2" to="/orders">Orders</Link>}

        {!token ? (
          <>
            <Link className="btn btn-outline-light me-2" to="/login">Login</Link>
            <Link className="btn btn-outline-light" to="/register">Register</Link>
          </>
        ) : (
          <button className="btn btn-danger" onClick={handleLogout}>
            Logout
          </button>
        )}
      </div>
    </nav>
  );
}

export default Navbar;