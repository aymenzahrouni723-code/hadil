import { NavLink } from 'react-router-dom';

export default function Navbar({ alertCount }) {
  return (
    <nav className="navbar">
      <NavLink to="/" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} end>
        <span className="nav-icon">🌿</span>
        <span>Dashboard</span>
      </NavLink>
      <NavLink to="/control" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
        <span className="nav-icon">🎛️</span>
        <span>Contrôle</span>
      </NavLink>
      <NavLink to="/cultures" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
        <span className="nav-icon">🌱</span>
        <span>Cultures</span>
      </NavLink>
      <NavLink to="/history" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
        <span className="nav-icon">📈</span>
        <span>Historique</span>
      </NavLink>
      <NavLink to="/alerts" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
        <span className="nav-icon">🔔</span>
        {alertCount > 0 && <span className="nav-badge">{alertCount}</span>}
        <span>Alertes</span>
      </NavLink>
    </nav>
  );
}
