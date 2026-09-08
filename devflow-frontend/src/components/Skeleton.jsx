const Skeleton = ({ className = '' }) => (
  <div className={`animate-pulse bg-gray-700/60 rounded ${className}`} />
);

export default Skeleton;