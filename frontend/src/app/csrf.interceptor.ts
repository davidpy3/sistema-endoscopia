import { HttpInterceptorFn } from '@angular/common/http';

function readCookie(name: string): string | null {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) {
    return parts.pop()?.split(';').shift() ?? null;
  }
  return null;
}

export const csrfInterceptor: HttpInterceptorFn = (request, next) => {
  const method = request.method.toUpperCase();
  if (!['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
    return next(request);
  }

  const token = readCookie('csrftoken');
  if (!token) {
    return next(request);
  }

  return next(
    request.clone({
      setHeaders: {
        'X-CSRFToken': token,
      },
    })
  );
};
