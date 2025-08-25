import { Todo } from './model';
import { AuthContext } from "./AuthProvide";
import keycloak from "./keycloak";



const API_BASE_URL = 'http://localhost:5000/api';

export class TodoAPI {
  static async getAllTodos(token: string): Promise<Todo[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/todos`, {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${keycloak.token}`,
        },
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching todos:', error);
      throw error;
    }
  }

  static async createTodo(todoText: string): Promise<Todo> {
    try {
      const response = await fetch(`${API_BASE_URL}/todos`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          todo: todoText,
          isDone: false,
        }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error creating todo:', error);
      throw error;
    }
  }

  static async updateTodo(id: number, updates: Partial<Todo>): Promise<Todo> {
    try {
      const response = await fetch(`${API_BASE_URL}/todos/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updates),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error updating todo:', error);
      throw error;
    }
  }

  static async deleteTodo(id: number): Promise<Todo> {
    try {
      const response = await fetch(`${API_BASE_URL}/todos/${id}`, {
        method: 'DELETE',
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error deleting todo:', error);
      throw error;
    }
  }

  static async toggleTodo(id: number): Promise<Todo> {
    try {
      const response = await fetch(`${API_BASE_URL}/todos/${id}/toggle`, {
        method: 'PATCH',
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error toggling todo:', error);
      throw error;
    }
  }
}
