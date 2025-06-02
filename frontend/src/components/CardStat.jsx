const CardStat = ({ icon, label, value, bgColor }) => {
  return (
    <div className="bg-white h-[151px] rounded-30 p-4 shadow-md flex items-center gap-4 dark:bg-gray-800">
      {icon && (
        <div className={`${bgColor} w-[84px] h-[84px] p-2 flex items-center justify-center rounded-50 bg-blue-light`}>
          {icon}
        </div>
      )}
      <div>
        <div className="text-[14px] text-gray-light dark:text-white">{label}</div>
        <div className="text-[32px] font-bold text-black dark:text-white">{value}</div>
      </div>
    </div>
  );
};
export default CardStat;