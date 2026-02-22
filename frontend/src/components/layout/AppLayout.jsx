import Sidebar from './Sidebar';
import TopBar  from './TopBar';

// AppLayout wraps every protected page
// Usage: <AppLayout><Dashboard /></AppLayout>
export default function AppLayout({ children }) {
  return (
    <div
      style={{
        display:         'flex',
        minHeight:       '100vh',
        backgroundColor: '#050B18',
      }}
    >
      {/* Fixed left sidebar */}
      <Sidebar />

      {/* Main content area — offset by sidebar width */}
      <div
        style={{
          flex:       1,
          marginLeft: '240px',
          display:    'flex',
          flexDirection: 'column',
        }}
      >
        {/* Fixed top bar */}
        <TopBar />

        {/* Page content — offset by topbar height */}
        <main
          className="page-bg"
          style={{
            flex:       1,
            marginTop:  '64px',
            padding:    '28px',
            minHeight:  'calc(100vh - 64px)',
          }}
        >
          {children}
        </main>
      </div>
    </div>
  );
}