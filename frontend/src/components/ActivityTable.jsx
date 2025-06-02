import { useEffect, useState } from "react";
import Icon from "../icons/Icon";

const ActivityTable = () => {
  const [activities, setActivities] = useState([]);
  const [search, setSearch] = useState("");
  const [sort, setSort] = useState("desc");
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 5;
  const filteredActivities = activities.filter(
    (row) => row.verified_at !== null
  );
  const totalData = filteredActivities.length;
  const startIdx = (currentPage - 1) * itemsPerPage + 1;
  const endIdx = Math.min(currentPage * itemsPerPage, totalData);
  const currentItems = filteredActivities.slice(startIdx - 1, endIdx);

  useEffect(() => {
    const fetchData = async () => {
      const res = await fetch(
        `http://localhost:5000/api/activity?search=${search}&sort=${sort}`
      );
      const data = await res.json();
      setActivities(data);
    };
    fetchData();
  }, [search, sort]);

  return (
    <div className="bg-white p-6 rounded-30 shadow-md overflow-auto dark:bg-gray-800 ">
      <div className="flex flex-col md:flex-row md:items-center pt-6 px-6 justify-between mb-4">
        <div>
          <h3 className="text-2xl font-semibold mb-2 text-blue-dark dark:to-blue-dark">
            Aktivitas Terkini
          </h3>
          <p className="text-sm text-green-medium">
            Riwayat aktivitas verifikasi sertifikat.
          </p>
        </div>
        <div className="flex items-center gap-3 mt-4 md:mt-0">
          <div className="relative">
            <input
              type="text"
              placeholder="Cari"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="h-[48px] bg-default border border-blue-light rounded-10 px-3 py-2 pl-10 w-56 text-sm focus:outline-none focus:border-blue dark:bg-gray-800 dark:text-white dark:border-gray-600"
            />
            <span className="absolute left-3 top-3.5 text-gray-400">
              <Icon name="search" className="w-[20px] text-blue-dark " />
            </span>
          </div>
          <select
            value={sort}
            onChange={(e) => setSort(e.target.value)}
            className="h-[48px] bg-default border border-blue-light px-3 py-2 rounded-10 text-sm text-gray-dark focus:outline-none focus:border-blue dark:bg-gray-800 dark:text-gray-500 dark:border-gray-600"
          >
            <option value="desc">Sort by: Newest</option>
            <option value="asc">Sort by: Oldest</option>
          </select>
        </div>
      </div>

      <table className="w-full text-sm ">
        <thead className="text-left font-light text-gray-500">
          <tr>
            <th className="py-3 px-6">Certificate ID</th>
            <th className="py-3 px-6">Diverifikasi Pada</th>
            <th className="py-3 px-6">Keterangan</th>
            <th className="py-3 px-6">Status</th>
          </tr>
        </thead>
        <tbody>
          {currentItems.map((row, index) => (
            <tr
              key={index}
              className="border-t text-black hover:bg-blue-light dark:hover:bg-gray-700 dark:text-white"
            >
              <td className="py-3 px-6 font-medium">{row.certificate_id}</td>
              <td className="py-3 px-6">
                {row.verified_at
                  ? new Date(row.verified_at).toLocaleString()
                  : "-"}
              </td>
              <td className="py-3 px-6">
                <span
                  className={`px-3 py-1 text-[10px] font-semibold rounded-50 ${
                    row.status === "Valid"
                      ? "bg-green-light text-green-dark border-green-dark border-2"
                      : "bg-red-light border-2 border-red-dark text-red-dark"
                  } font-normal`}
                >
                  {row.status === "Valid"
                    ? "Sertifikat valid"
                    : "Sertifikat tidak valid"}
                </span>
              </td>
              <td className="py-3 px-6">
                <span
                  className={`px-3 py-1 text-[12px] font-semibold rounded-50 ${
                    row.status === "Valid"
                      ? "bg-green-light text-green-dark border-green-dark border-2"
                      : "bg-red-light border-2 border-red-dark text-red-dark"
                  }`}
                >
                  {row.status === "Valid" ? "Success" : "Issued"}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="text-sm text-gray-light mt-4 flex items-center justify-between">
        <span>
          Showing data {startIdx} to {endIdx} of {totalData} entries
        </span>

        <div className="flex gap-1">
          {[
            ...Array(
              Math.ceil(
                activities.filter((row) => row.verified_at !== null).length /
                  itemsPerPage
              )
            ).keys(),
          ].map((page) => (
            <button
              key={page}
              onClick={() => setCurrentPage(page + 1)}
              className={`px-3 py-1 rounded-5 border text-sm ${
                page + 1 === currentPage
                  ? "bg-blue-dark text-blue-light dark:bg-blue-light dark:text-blue-dark"
                  : "text-gray-dark dark:text-gray-500 hover:bg-blue-light hover:text-blue-dark"
              }`}
            >
              {page + 1}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ActivityTable;
