/* ============================================================
   auth.js — shared across every protected page
   Responsibilities:
   1. Block access immediately if there's no token (redirect to login.html)
   2. Verify the token with the backend and populate navbar user info
   3. Wire up the Sign out button
   4. Wire up the profile dropdown (hover to preview, click to pin/unpin)
   5. Apply + persist the selected accent theme
   ============================================================ */

const API_BASE = 'http://127.0.0.1:8000'; // update to your FastAPI server URL

function getToken(){
  return sessionStorage.getItem('token');
}

/** Decodes a JWT's payload without verifying it (just reading claims client-side). */
function parseJwt(token){
  try{
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const json = decodeURIComponent(atob(base64).split('').map(c =>
      '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)
    ).join(''));
    return JSON.parse(json);
  } catch(err){
    return null;
  }
}

function applyDisplayName(name){
  if(!name) return;
  document.querySelectorAll('.user-name').forEach(el => el.textContent = name);
  document.querySelectorAll('.user-avatar').forEach(el => el.textContent = name.charAt(0).toUpperCase());
}

/* Runs immediately (not waiting for DOMContentLoaded) so a logged-out
   user never even sees the page flash before redirecting. */
(function guard(){
  if(!getToken()){
    window.location.href = 'login.html';
  }
})();

async function verifyAndLoadUser(){
  // Immediate fallback: read the username straight off the JWT's own claims
  // so the navbar is correct even before /auth/me responds (or if it's not built yet).
  const claims = parseJwt(getToken());
  if(claims){
    applyDisplayName(claims.user_name || claims.username || claims.sub || null);
  }

  try{
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: { 'Authorization': `Bearer ${getToken()}` }
    });

    if(res.status === 401){
      sessionStorage.removeItem('token');
      window.location.href = 'login.html';
      return;
    }

    if(!res.ok) return; // keep the JWT-derived name already applied above

    const data = await res.json();
    applyDisplayName(data.user_name || data.username || null);
  } catch(err){
    console.error('Auth check failed:', err);
  }
}

function signOut(){
  sessionStorage.removeItem('token');
  window.location.href = 'login.html';
}

/* ---------------- theme ---------------- */
function applyTheme(theme){
  document.documentElement.setAttribute('data-theme', theme);
  document.querySelectorAll('.theme-dot').forEach(dot => {
    dot.classList.toggle('active', dot.dataset.theme === theme);
  });
  localStorage.setItem('theme', theme);
}

document.addEventListener('DOMContentLoaded', () => {
  verifyAndLoadUser();

  const btn = document.getElementById('signOutBtn');
  if(btn) btn.addEventListener('click', signOut);

  applyTheme(localStorage.getItem('theme') || 'green');

  /* ---------------- profile dropdown ---------------- */
  const profileMenu = document.getElementById('profileMenu');
  const profileTrigger = document.getElementById('profileTrigger');

  if(profileTrigger){
    profileTrigger.addEventListener('click', (e) => {
      e.stopPropagation(); // don't let the outside-click handler fire on this same click
      profileMenu.classList.toggle('pinned');
    });
  }

  // clicking anywhere outside the menu closes a pinned dropdown
  document.addEventListener('click', (e) => {
    if(profileMenu && !profileMenu.contains(e.target)){
      profileMenu.classList.remove('pinned');
    }
  });

  document.querySelectorAll('.theme-dot').forEach(dot => {
    dot.addEventListener('click', (e) => {
      e.stopPropagation();
      applyTheme(dot.dataset.theme);
    });
  });
});
