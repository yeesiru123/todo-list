import React, { useState, useEffect, createContext, ReactNode } from "react";
import keycloak from "./keycloak";

interface AuthContextType {
  isAuthenticated: boolean;
  token?: string;
  login: () => void;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    keycloak.init({ onLoad: "login-required" }).then((authenticated) => {
      setIsAuthenticated(authenticated);
        if (authenticated) {
            keycloak.loadUserInfo().then((userInfo) => {
            console.log("User Info:", userInfo);
            });
        }
    });
  }, []);

  const login = () => keycloak.login();
  const logout = () => keycloak.logout();

  return (
    <AuthContext.Provider value={{ isAuthenticated, token: keycloak.token, login, logout }}>
      {isAuthenticated ? children : <div>Loading...</div>}
    </AuthContext.Provider>
  );
};
