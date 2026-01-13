import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// 需要登录才能访问的路径
const protectedPaths = [
  "/",
  "/categories",
  "/products",
  "/leaderboard",
  "/assistant",
  "/settings",
  "/about",
];

// 已登录用户不应访问的路径（登录/注册页）
const authPaths = ["/auth/sign-in", "/auth/sign-up", "/auth/forgot-password"];

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // 获取 session token
  const sessionToken = request.cookies.get("auth_token")?.value;

  const isProtectedPath = protectedPaths.some(
    (path) => pathname === path || (path !== "/" && pathname.startsWith(path))
  );
  const isAuthPath = authPaths.some((path) => pathname.startsWith(path));

  // 未登录用户访问受保护页面 -> 重定向到登录页
  if (isProtectedPath && !sessionToken) {
    const signInUrl = new URL("/auth/sign-in", request.url);
    signInUrl.searchParams.set("callbackUrl", pathname);
    return NextResponse.redirect(signInUrl);
  }

  // 已登录用户访问登录/注册页 -> 重定向到首页
  if (isAuthPath && sessionToken) {
    return NextResponse.redirect(new URL("/", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * 匹配所有路径除了:
     * - api 路由
     * - _next 静态文件
     * - 静态资源
     */
    "/((?!api|_next/static|_next/image|favicon.ico|.*\\..*|auth/reset-password|auth/verify-email).*)",
  ],
};
