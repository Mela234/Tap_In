import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

function Success() {
  const navigate = useNavigate();

  useEffect(() => {
    // Give backend a second to process webhook
    const timer = setTimeout(() => {
      navigate("/weekly");
    }, 2000);

    return () => clearTimeout(timer);
  }, [navigate]);

  return <h2>Payment successful 🎉 Activating your access...</h2>;
}

export default Success;
