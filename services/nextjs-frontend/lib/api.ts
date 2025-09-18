
import { Ticket } from "./mock-data";
import { useAuthStore } from "./store";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:9090";

export async function getTickets(): Promise<any[]> {
  const token = useAuthStore.getState().token;

  if (!token) {
    throw new Error("No authentication token found.");
  }

  try {
    const response = await fetch(`${API_URL}/api/v1/tickets`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error("Failed to fetch tickets.");
    }

    const data = await response.json();
    console.log("Tickets from API:", data);
    return data.tickets || [];
  } catch (error) {
    console.error("Failed to fetch tickets:", error);
    return [];
  }
}

export async function getTicketById(id: string): Promise<any> {
  const token = useAuthStore.getState().token;

  if (!token) {
    throw new Error("No authentication token found.");
  }

  try {
    const response = await fetch(`${API_URL}/api/v1/tickets/${id}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error("Failed to fetch ticket.");
    }

    const data = await response.json();
    console.log("Ticket from API:", data);
    return data;
  } catch (error) {
    console.error("Failed to fetch ticket:", error);
    return null;
  }
}

export async function escalateTicket(id: string, reason: string): Promise<any> {
  const token = useAuthStore.getState().token;

  if (!token) {
    throw new Error("No authentication token found.");
  }

  try {
    const response = await fetch(`${API_URL}/api/v1/tickets/${id}/escalate?reason=${encodeURIComponent(reason)}`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error("Failed to escalate ticket.");
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Failed to escalate ticket:", error);
    return null;
  }
}

export const createChatSession = async (userEmail: string): Promise<string> => {
  try {
    const adkApiBaseUrl = process.env.NEXT_PUBLIC_ADK_API_URL || 'http://localhost:8010';
    const userId = userEmail.replace(/[@.]/g, '_');
    const response = await fetch(
      `${adkApiBaseUrl}/apps/AURA/users/${userId}/sessions`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({
          state: {},
          events: [],
        }),
      }
    );
    const data = await response.json();
    return data.id;
  } catch (error) {
    console.error('Error creating chat session:', error);
    throw error;
  }
};


export async function getDepartments(): Promise<any[]> {
  const token = useAuthStore.getState().token;

  if (!token) {
    throw new Error("No authentication token found.");
  }

  try {
    const response = await fetch(`${API_URL}/api/v1/users/departments/`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error("Failed to fetch departments.");
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Failed to fetch departments:", error);
    return [];
  }
}

export async function createTicket(ticketData: any): Promise<any> {
  const token = useAuthStore.getState().token;

  if (!token) {
    throw new Error("No authentication token found.");
  }

  const formData = new FormData();
  for (const key in ticketData) {
    if (key === 'files') {
      for (const file of ticketData[key]) {
        formData.append('files', file);
      }
    } else {
      formData.append(key, ticketData[key]);
    }
  }

  try {
    const response = await fetch(`${API_URL}/api/v1/tickets/`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    });

    if (!response.ok) {
      throw new Error("Failed to create ticket.");
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Failed to create ticket:", error);
    return null;
  }
}
