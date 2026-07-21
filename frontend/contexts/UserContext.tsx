"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import toast from "react-hot-toast";
import * as api from "@/lib/api";
import type { UserResponse } from "@/lib/types";
import { useAuth } from "./AuthContext";

interface UserContextValue {
  user: UserResponse | null;
  isLoading: boolean;
  refreshUser: () => Promise<void>;
  updateCompanyName: (companyName: string) => Promise<void>;
}

const UserContext = createContext<UserContextValue | undefined>(undefined);

export function UserProvider({ children }: { children: ReactNode }) {
  const { isAuthenticated } = useAuth();
  const [user, setUser] = useState<UserResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  async function refreshUser() {
    if (!isAuthenticated) {
      setUser(null);
      return;
    }
    setIsLoading(true);
    try {
      const me = await api.getMe();
      setUser(me);
    } catch {
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    refreshUser();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated]);

  async function updateCompanyName(companyName: string) {
    const updated = await api.updateMe(companyName);
    setUser(updated);
    toast.success("정보가 저장되었습니다");
  }

  return (
    <UserContext.Provider value={{ user, isLoading, refreshUser, updateCompanyName }}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser(): UserContextValue {
  const ctx = useContext(UserContext);
  if (!ctx) throw new Error("useUser must be used within UserProvider");
  return ctx;
}
