const NotFoundPage = () => {
  return (
    <div style={{ 
      padding: 'var(--space-2xl)', 
      textAlign: 'center',
      minHeight: '60vh',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center'
    }}>
      <h1 style={{ fontSize: '4rem', color: 'var(--accent-primary)' }}>404</h1>
      <h2>Page Not Found</h2>
      <p>The page you're looking for doesn't exist.</p>
      <div style={{ marginTop: 'var(--space-xl)' }}>
        <a href="/" className="btn btn-primary">
          Go Home
        </a>
      </div>
    </div>
  );
};

export default NotFoundPage;
