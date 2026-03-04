import React, { useEffect, useState } from 'react';

type SessionState = {
  authenticated: boolean;
};

const BFF_BASE_URL = process.env.REACT_APP_BFF_BASE_URL || 'http://localhost:8001';
const REPORT_BASE_URL = process.env.REACT_APP_REPORT_BASE_URL || 'http://localhost:8002';

const ReportPage: React.FC = () => {
  const [initialized, setInitialized] = useState(false);
  const [authenticated, setAuthenticated] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    (async () => {
      try {
        const res = await fetch(`${BFF_BASE_URL}/auth/session`, {
          method: 'GET',
          credentials: 'include',
        });

        if (cancelled) return;

        if (res.ok) {
          const data = (await res.json()) as SessionState;
          setAuthenticated(Boolean(data.authenticated));
        } else {
          setAuthenticated(false);
        }
      } catch {
        if (!cancelled) setAuthenticated(false);
      } finally {
        if (!cancelled) setInitialized(true);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, []);

  const login = () => {
    window.location.href = `${BFF_BASE_URL}/auth/login`;
  };

  const logout = () => {
    window.location.href = `${BFF_BASE_URL}/auth/logout`;
  };

  const downloadReport = async () => {
    try {
      setLoading(true);
      setError(null);
        const r1 = await fetch(`${REPORT_BASE_URL}/api/reports`, {
            method: 'GET',
            credentials: 'include',
            headers: {'Accept': 'application/json'},
        });

        if (r1.status === 401) {
            setAuthenticated(false);
            setError('Not authenticated');
            return;
        }
        if (!r1.ok) throw new Error(`Failed: ${r1.status}`);

        const {url: cdnUrl, filename: apiFilename} = await r1.json();

        const r2 = await fetch(cdnUrl, {
            method: 'GET',
            mode: 'cors',
        });
        if (!r2.ok) throw new Error(`CDN failed: ${r2.status}`);

        const blob = await r2.blob();

        const cd = r2.headers.get('content-disposition') || '';
        const m = cd.match(/filename\*?=(?:UTF-8'')?"?([^";]+)"?/i);
        const filename = apiFilename ?? m?.[1] ?? 'report.pdf';

        const objUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = objUrl;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(objUrl);
      } catch (err) {
         setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
     }
  };

  if (!initialized) {
    return <div>Loading...</div>;
  }

  if (!authenticated) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100">
        <button
          onClick={() => login()}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Login
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100">
      <div className="p-8 bg-white rounded-lg shadow-md">
        <h1 className="text-2xl font-bold mb-6">Usage Reports</h1>

        <button
          onClick={downloadReport}
          disabled={loading}
          className={`px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 ${
            loading ? 'opacity-50 cursor-not-allowed' : ''
          }`}
        >
          {loading ? 'Generating Report...' : 'Download Report'}
        </button>

        <button
          onClick={() => logout()}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Logout
        </button>

        {error && (
          <div className="mt-4 p-4 bg-red-100 text-red-700 rounded">
            {error}
          </div>
        )}
      </div>
    </div>
  );
};

export default ReportPage;
