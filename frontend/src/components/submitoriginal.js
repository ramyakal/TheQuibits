import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';

const Submit = () => {
  const location = useLocation();
  const [res, setRes] = useState(null);

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const prediction = params.get('prediction');
    if (prediction) {
      setRes(JSON.parse(decodeURIComponent(prediction)));
    }
  }, [location]);

  return (
    <div>
      {res && (
        <div className='result'>
          {}
          {res.Prediction === 'Malicious' && (
            <p>
              Oops! There seems to be something wrong with your network!<br /> Consider disconnecting it!
            </p>
          )}
          {res.Prediction !== 'Malicious' && (
            <p>
              Hurray!! Your Network is safe!<br /> Have a nice day
            </p>
          )}
        </div>
      )}
    </div>
  );
};

export default Submit;
