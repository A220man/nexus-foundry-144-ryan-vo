import { Routes, Route, Link } from 'react-router-dom';
import { JobList } from './components/JobList';
import { JobForm } from './components/JobForm';
import { JobDetail } from './pages/JobDetail';

function Header() {
  return (
    <header style={{
      background: 'white',
      borderBottom: '1px solid #e5e7eb',
      padding: '1rem 0',
      position: 'sticky',
      top: 0,
      zIndex: 100,
    }}>
      <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Link to="/" style={{ fontSize: '1.5rem', fontWeight: 700, color: '#1a1a2e' }}>
          Nexus Foundry
        </Link>
        <nav style={{ display: 'flex', gap: '1.5rem' }}>
          <Link to="/" style={{ fontWeight: 500 }}>Jobs</Link>
          <Link to="/create" style={{ fontWeight: 500 }}>Create Job</Link>
        </nav>
      </div>
    </header>
  );
}

function Footer() {
  return (
    <footer style={{ marginTop: '3rem', padding: '2rem 0', borderTop: '1px solid #e5e7eb', textAlign: 'center', color: '#6b7280' }}>
      <div className="container">
        <p>Nexus Foundry - Write HTML. Render video. Built for agents.</p>
        <p style={{ fontSize: '0.875rem', marginTop: '0.5rem' }}>Ryan Vo &lt;ryandtvo@gmail.com&gt;</p>
      </div>
    </footer>
  );
}

function App() {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Header />
      <main className="container" style={{ flex: 1, paddingTop: '2rem', paddingBottom: '2rem' }}>
        <Routes>
          <Route path="/" element={<JobList />} />
          <Route path="/create" element={<JobForm onSuccess={(id) => window.location.href = `/jobs/${id}`} />} />
          <Route path="/jobs/:id" element={<JobDetail />} />
        </Routes>
      </main>
      <Footer />
    </div>
  );
}

export default App;
