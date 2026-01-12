"use client";

/**
 * User API Client
 * 
 * 调用后端用户管理 API
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

// ============================================================================
// Types
// ============================================================================

export interface UserProfile {
  id: string;
  email: string;
  name: string | null;
  image: string | null;
  plan: string;
  emailVerified: boolean;
  createdAt: string | null;
}

export interface UsageStats {
  total_sessions: number;
  total_messages: number;
  total_tokens: number;
  total_cost: number;
  daily_chat_used: number;
  daily_chat_limit: number;
}

export interface UserSession {
  session_id: string;
  title: string | null;
  message_count: number;
  turn_count: number;
  created_at: string | null;
  updated_at: string | null;
  last_message_at: string | null;
  is_archived: boolean;
}

// ============================================================================
// Profile APIs
// ============================================================================

export async function getProfile(): Promise<UserProfile | null> {
  try {
    const res = await fetch(`${API_BASE}/api/user/profile`, {
      credentials: "include",
    });
    
    if (!res.ok) {
      return null;
    }
    
    return res.json();
  } catch {
    return null;
  }
}

export async function updateProfile(data: { name?: string; image?: string }): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/api/user/profile`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(data),
    });
    
    return res.ok;
  } catch {
    return false;
  }
}

// ============================================================================
// Usage APIs
// ============================================================================

export async function getUsage(): Promise<UsageStats | null> {
  try {
    const res = await fetch(`${API_BASE}/api/user/usage`, {
      credentials: "include",
    });
    
    if (!res.ok) {
      return null;
    }
    
    return res.json();
  } catch {
    return null;
  }
}

// ============================================================================
// Session APIs
// ============================================================================

export async function getUserSessions(options?: {
  limit?: number;
  offset?: number;
  includeArchived?: boolean;
}): Promise<{ sessions: UserSession[]; total: number } | null> {
  try {
    const params = new URLSearchParams();
    if (options?.limit) params.set("limit", String(options.limit));
    if (options?.offset) params.set("offset", String(options.offset));
    if (options?.includeArchived) params.set("include_archived", "true");
    
    const res = await fetch(`${API_BASE}/api/user/sessions?${params}`, {
      credentials: "include",
    });
    
    if (!res.ok) {
      return null;
    }
    
    return res.json();
  } catch {
    return null;
  }
}

export async function claimSessions(sessionIds: string[]): Promise<{ claimed: number } | null> {
  try {
    const res = await fetch(`${API_BASE}/api/user/sessions/claim`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ session_ids: sessionIds }),
    });
    
    if (!res.ok) {
      return null;
    }
    
    return res.json();
  } catch {
    return null;
  }
}

export async function transferSession(sessionId: string): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/api/user/sessions/${sessionId}/transfer`, {
      method: "POST",
      credentials: "include",
    });
    
    return res.ok;
  } catch {
    return false;
  }
}

// ============================================================================
// Account APIs
// ============================================================================

export async function deleteAccount(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/api/user/account`, {
      method: "DELETE",
      credentials: "include",
    });
    
    return res.ok;
  } catch {
    return false;
  }
}
