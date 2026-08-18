import { createAuthenticatedDatabaseClient } from '@edu-hub/database';
import { createClient, type Session } from '@supabase/supabase-js';
import { SUPABASE_PUBLISHABLE_KEY, SUPABASE_URL } from 'astro:env/server';
import type { APIContext, AstroGlobal } from 'astro';

type Context = APIContext | AstroGlobal;
const accessCookie = 'edu-hub-access-token';
const refreshCookie = 'edu-hub-refresh-token';

function setSessionCookies(context: Context, session: Session) {
  const options = {
    httpOnly: true,
    sameSite: 'strict' as const,
    secure: import.meta.env.PROD,
    path: '/',
  };
  context.cookies.set(accessCookie, session.access_token, {
    ...options,
    maxAge: session.expires_in,
  });
  context.cookies.set(refreshCookie, session.refresh_token, {
    ...options,
    maxAge: 60 * 60 * 24 * 30,
  });
}
export function clearSessionCookies(context: Context) {
  context.cookies.delete(accessCookie, { path: '/' });
  context.cookies.delete(refreshCookie, { path: '/' });
}
export async function establishSession(
  context: Context,
  email: string,
  password: string,
) {
  const auth = createClient(SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY, {
    auth: { persistSession: false, autoRefreshToken: false },
  });
  const result = await auth.auth.signInWithPassword({ email, password });
  if (result.data.session) setSessionCookies(context, result.data.session);
  return result;
}
export async function getStaffContext(context: Context) {
  let accessToken = context.cookies.get(accessCookie)?.value;
  const refreshToken = context.cookies.get(refreshCookie)?.value;
  if (!accessToken && !refreshToken) return null;
  let client = accessToken
    ? createAuthenticatedDatabaseClient(
        { SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY },
        accessToken,
      )
    : null;
  let userResult =
    client && accessToken ? await client.auth.getUser(accessToken) : null;
  if (
    (!userResult || userResult.error || !userResult.data.user) &&
    refreshToken
  ) {
    const auth = createClient(SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY, {
      auth: { persistSession: false, autoRefreshToken: false },
    });
    const refreshed = await auth.auth.refreshSession({
      refresh_token: refreshToken,
    });
    if (!refreshed.data.session) {
      clearSessionCookies(context);
      return null;
    }
    setSessionCookies(context, refreshed.data.session);
    accessToken = refreshed.data.session.access_token;
    client = createAuthenticatedDatabaseClient(
      { SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY },
      accessToken,
    );
    userResult = await client.auth.getUser(accessToken);
  }
  if (!client || !userResult || userResult.error || !userResult.data.user) {
    clearSessionCookies(context);
    return null;
  }
  const { data: staff } = await client
    .from('staff_users')
    .select('role,status')
    .eq('user_id', userResult.data.user.id)
    .maybeSingle();
  if (!staff || staff.status !== 'active') {
    clearSessionCookies(context);
    return null;
  }
  return { client, user: userResult.data.user, staff };
}
export async function signOut(context: Context) {
  const accessToken = context.cookies.get(accessCookie)?.value;
  if (accessToken) {
    const client = createAuthenticatedDatabaseClient(
      { SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY },
      accessToken,
    );
    await client.auth.signOut({ scope: 'local' });
  }
  clearSessionCookies(context);
}
