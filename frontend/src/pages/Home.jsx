import { useEffect, useState } from "react";
import CardStat from "../components/CardStat";
import ActivityTable from "../components/ActivityTable";
import Icon from "../icons/Icon";

const Home = () => {
  const [activities, setActivities] = useState([]);
  const [totalCertificates, setTotalCertificates] = useState(0);
  const [totalVerified, setTotalVerified] = useState(0);

  useEffect(() => {
    const fetchData = async () => {
      const res = await fetch("http://localhost:5000/api/activity");
      const data = await res.json();
      setActivities(data);
      setTotalCertificates(data.length);
      setTotalVerified(data.filter((item) => item.verified_at !== null).length);
    };
    fetchData();
  }, []);

    return (
      <div className="space-y-6 px-6 py-4 pb-8 dark:bg-gray-900 ">
        <div className="flex flex-col md:flex-row justify-between items-start gap-6 px-6 py-4">
          <div className="flex-1 max-w-[700px]">
            <h2 className="text-[50px] font-bold text-blue-dark mb-4">
              Welcome to CertGuard
            </h2>
            <h4 className="text-[30px] font-semibold text-gray-900 mb-4 dark:text-blue-light">
              Lindungi dan Verifikasi Sertifikat Digital Anda dengan Teknologi
              Blockchain
            </h4>
            <p className="text-gray-600 text-[20px] leading-relaxed dark:text-gray-400">
              CertGuard adalah solusi inovatif untuk memastikan keaslian
              sertifikat pelatihan digital Anda. Dengan memanfaatkan teknologi
              blockchain yang aman dan terdesentralisasi, CertGuard memberikan
              perlindungan maksimal terhadap pemalsuan dan manipulasi
              sertifikat.
            </p>
          </div>
          <div className="max-w-[500px] shrink-0 self-start -mt-1">
            <img
              src="/laptop-verifikasi.png"
              alt="Illustration"
              className="w-full"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <CardStat
            icon={
              <Icon
                name="document"
                className="h-[44px] text-blue-dark dark:text-blue-light"
              />
            }
            label="Sertifikat Terbit"
            value={totalCertificates}
          />
          <CardStat
            icon={
              <Icon
                name="document_verified"
                className="h-[44px] text-blue-dark dark:text-blue-light"
              />
            }
            label="Sertifikat Terverifikasi"
            value={totalVerified}
          />
        </div>

        <div className="mt-6">
          <ActivityTable />
        </div>
      </div>
    );
  };

export default Home;
