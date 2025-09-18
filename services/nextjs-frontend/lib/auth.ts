export interface User {
  id: string
  name: string
  email: string
  role: "end-user" | "l1-engineer" | "l2-engineer" | "ops-manager" | "transition-manager" | "admin"
  avatar?: string
}

export interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:9090";

export async function authenticateUser(email: string, password: string): Promise<{ user: User; token: string } | null> {
  try {
    const response = await fetch(`${API_URL}/api/v1/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams({
        username: email,
        password: password,
      }),
    });

    if (!response.ok) {
      return null;
    }

    const data = await response.json();
    
    const user: User = {
      id: data.user.id,
      name: data.user.name,
      email: data.user.email,
      role: data.user.role,
      avatar: data.user.avatar,
    };

    return {
      user: user,
      token: data.access_token,
    };
  } catch (error) {
    console.error("Authentication failed:", error);
    return null;
  }
}