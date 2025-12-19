import axios from "axios";
import { type POIResponse } from "../types";

const instance = axios.create({
  baseURL: import.meta.env.VITE_BASE_URL || "http://localhost:8000",
  headers: {
    "Content-Type": "application/json",
  },
})

export const mutatePlan = async (input: string): Promise<POIResponse | null> => {
  try {
    const res = await instance("/api/chat-plan", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      data: {
        query: input
      }
    });
    return res.data as POIResponse; 
  } catch (error) {
    console.error("Error in mutatePlan:", error);
    return null;
  }
}

export const fetchHistory = async (id: number): Promise<POIResponse | null> => {
  try {
    const res = await instance.get(`/api/history/${id}`);
    return res.data as POIResponse;
  } catch (error) {
    console.error("Error in fetchHistory:", error);
    throw null;
  }
}