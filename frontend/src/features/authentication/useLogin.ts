import { useMutation, useQueryClient } from "@tanstack/react-query";
import { login as loginApi, LoginArgs } from "../../services/apiAuth";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";

export const useLogin = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const {
    mutate: login,
    data: user,
    isPending: isLoading,
    error,
  } = useMutation({
    mutationFn: ({ email, password }: LoginArgs) =>
      loginApi({ email, password }),
    onSuccess: (user) => {
      queryClient.setQueryData(["user"], user);
      navigate("/home");
    },
    onError: () => {
      toast.error("Error with login");
    },
  });

  return { login, user, isLoading, error };
};
