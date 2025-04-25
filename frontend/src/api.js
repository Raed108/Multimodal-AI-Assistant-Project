import axios from "axios";

export const generateResponse = async (question, constraints) => {
  const res = await axios.post("http://localhost:8000/generate_response/", { question, constraints });
  return res.data.response;
};
