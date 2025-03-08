import { useQuery } from "@tanstack/react-query";
import { getMe } from "../../services/apiAuth";

export const useUser = () => {
  const {
    data: user,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ["user"],
    queryFn: getMe,
    retry: 1,
    staleTime: 0,
  });

  return { user, isLoading, error, refetch };
};
