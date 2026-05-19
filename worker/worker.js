const GEMINI_API_KEY = 'AIzaSyBv6nYLyxsM_fo9p0hEilcECNVzCAPKzUc';
const SUPABASE_URL = 'https://mtahebtububylnmauzsa.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im10YWhlYnR1YnVieWxubWF1enNhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY4MTc3NjQsImV4cCI6MjA5MjM5Mzc2NH0.Lm3N5d9xd_HAGKesQzHJXwho_xqHjZ705kvhhlEZoAo';
const ALLOWED_ORIGIN = 'https://Tinho2508.github.io';
const MODEL = 'gemini-2.0-flash-lite';

export default {
  async fetch(request) {
    const origin = request.headers.get('Origin') || '';
    if (origin && origin !== ALLOWED_ORIGIN) {
      return new Response('Forbidden', { status: 403 });
    }
    const url = new URL(request.url);
    if (url.pathname === '/config' && request.method === 'GET') {
      return new Response(JSON.stringify({
        supabaseUrl: SUPABASE_URL,
        supabaseAnonKey: SUPABASE_ANON_KEY
      }), {
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': ALLOWED_ORIGIN
        }
      });
    }
    if (request.method !== 'POST') {
      return new Response('Method not allowed', { status: 405 });
    }
    try {
      const body = await request.json();
      const model = body.model || MODEL;
      const geminiUrl = 'https://generativelanguage.googleapis.com/v1beta/models/' + model + ':generateContent?key=' + GEMINI_API_KEY;
      delete body.model;
      const resp = await fetch(geminiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      const data = await resp.json();
      return new Response(JSON.stringify(data), {
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': ALLOWED_ORIGIN,
          'Access-Control-Allow-Methods': 'GET, POST',
          'Access-Control-Allow-Headers': 'Content-Type'
        }
      });
    } catch (e) {
      return new Response(JSON.stringify({ error: e.message }), { status: 500 });
    }
  }
};
