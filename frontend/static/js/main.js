/* ==========================================
   Вспомогательные функции
   ========================================== */

// Получить CSRF-токен из cookie
function getCookie(name) {
  let value = '; ' + document.cookie;
  let parts = value.split('; ' + name + '=');
  if (parts.length === 2) return parts.pop().split(';').shift();
}

// Форматирование плейсхолдера: FULL_NAME -> Full Name
function formatLabel(placeholder) {
  return placeholder
    .replace(/_/g, ' ')
    .toLowerCase()
    .replace(/\b\w/g, c => c.toUpperCase());
}

/* ==========================================
   Toast-уведомления
   ========================================== */

function showToast(message, type = 'success') {
  const container = document.getElementById('toast-container');
  if (!container) {
    const div = document.createElement('div');
    div.id = 'toast-container';
    div.className = 'toast-container';
    document.body.appendChild(div);
  }
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  document.getElementById('toast-container').appendChild(toast);
  setTimeout(() => toast.remove(), 4000);
}

/* ==========================================
   Обёртка fetch с CSRF и обработкой ошибок
   ========================================== */

async function apiRequest(url, options = {}) {
  const defaultHeaders = {
    'Content-Type': 'application/json',
    'X-CSRFToken': getCookie('csrftoken'),
  };

  const config = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };

  try {
    const res = await fetch(url, config);
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      const msg = err.error || err.detail || `Ошибка ${res.status}`;
      showToast(msg, 'error');
      throw new Error(msg);
    }
    return res;
  } catch (e) {
    if (e.name === 'TypeError') {
      showToast('Нет соединения с сервером', 'error');
    }
    throw e;
  }
}

/* ==========================================
   Выход из системы
   ========================================== */

async function logout() {
  try {
    await fetch('/api/auth/logout/', {
      method: 'POST',
      headers: { 'X-CSRFToken': getCookie('csrftoken') },
    });
  } catch (e) {}
  window.location.href = '/login/';
}

/* ==========================================
   Инициализация toast-контейнера
   ========================================== */
document.addEventListener('DOMContentLoaded', () => {
  if (!document.getElementById('toast-container')) {
    const div = document.createElement('div');
    div.id = 'toast-container';
    div.className = 'toast-container';
    document.body.appendChild(div);
  }
});