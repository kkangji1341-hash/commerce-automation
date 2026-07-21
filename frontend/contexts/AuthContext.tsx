"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import * as api from "@/lib/api";
import type { LoginInput, SignupInput } from "@/lib/types";

interface AuthContextValue {
  isAuthenticated: boolean;
  isInitializing: boolean;
  signup: (input: SignupInput) => Promise<void>;
  login: (input: LoginInput) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isInitializing, setIsInitializing] = useState(true);

  useEffect(() => {
    setIsAuthenticated(!!api.getAccessToken());
    setIsInitializing(false);
  }, []);

  async function signup(input: SignupInput) {
    await api.signUp(input);
    await login({ email: input.email, password: input.password });
  }

  async function login(input: LoginInput) {
    await api.login(input);
    setIsAuthenticated(true);
  }

  function logout() {
    api.logout();
    setIsAuthenticated(false);
  }

  return (
    <AuthContext.Provider value={{ isAuthenticated, isInitializing, signup, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
