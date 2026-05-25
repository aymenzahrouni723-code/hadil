import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import Control from './pages/Control';
import Cultures from './pages/Cultures';
import History from './pages/History';
import Alerts from './pages/Alerts';

function App() {
  const [alertCount, setAlertCount] = useState(0);

  // Vérifier le nombre d'alertes non acquittées
  useEffect(() => {
    const fetchAlertCount = async () => {
      try {
        const res = await fetch('/api/system/status');
        const data = await res.json();
        setAlertCount(data.unread_alerts || 0);
      } catch (err) {
        // Backend pas encore démarré
      }
    };

    fetchAlertCount();
    const interval = setInterval(fetchAlertCount, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <Router>
      <div className="app-container">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/control" element={<Control />} />
          <Route path="/cultures" element={<Cultures />} />
          <Route path="/history" element={<History />} />
          <Route path="/alerts" element={<Alerts />} />
        </Routes>
      </div>
      <Navbar alertCount={alertCount} />
    </Router>
  );
}

export default App;
