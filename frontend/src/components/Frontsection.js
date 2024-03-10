import React from "react";
import "./Frontsection.css";
const Frontsection = ({ user }) => {
  const href1 = user ? "/scan" : "/signup";
  return (
    <div className="frontpage">
      <a href={href1} className="trynow-button1">
        Try now
      </a>
    </div>
  );
};

export default Frontsection;

const styles = {
  secimg: {
    width: "90%",
    height: "auto",
    borderRadius: "0.5em",
  },
};
