import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import CardStat from "../components/CardStat";
import ActivityTable from "../components/ActivityTable";
import Icon from "../icons/Icon";

const Home = () => {
  const [totalTerbit, setTotalTerbit] = useState(0);
  const [totalVerified, setTotalVerified] = useState(0);
  const [totalBelumVerifikasi, setTotalBelumVerifikasi] = useState(0);
  const fullText =
    "Lindungi dan Verifikasi Sertifikat Digital Anda dengan Teknologi Blockchain!";
  const [displayedText, setDisplayedText] = useState("");
  const [index, setIndex] = useState(0);
  const [direction, setDirection] = useState("forward");

  useEffect(() => {
    // Fetch statistik dari endpoint
    const fetchStats = async () => {
      try {
        const [res1, res2, res3] = await Promise.all([
          fetch("http://localhost:5000/api/total_terbit"),
          fetch("http://localhost:5000/api/total_terverifikasi"),
          fetch("http://localhost:5000/api/total_belum_verifikasi"),
        ]);

        const data1 = await res1.json();
        const data2 = await res2.json();
        const data3 = await res3.json();

        setTotalTerbit(data1.total || 0);
        setTotalVerified(data2.total || 0);
        setTotalBelumVerifikasi(data3.total || 0);
      } catch (err) {
        console.error("Gagal fetch data statistik:", err);
      }
    };

    fetchStats();
  }, []);

  // Animasi mengetik teks
  useEffect(() => {
    const typingSpeed = 30;
    const resetDelay = 2000;

    const timer = setTimeout(() => {
      if (direction === "forward") {
        if (index < fullText.length) {
          setDisplayedText(fullText.slice(0, index + 1));
          setIndex(index + 1);
        } else {
          setDirection("reset");
          setTimeout(() => {
            setDisplayedText("");
            setIndex(0);
            setDirection("forward");
          }, resetDelay);
        }
      }
    }, typingSpeed);

    return () => clearTimeout(timer);
  }, [index, direction]);

  return (
    <div className="space-y-6 px-14 py-7 pb-8 dark:bg-gray-900 min-h-screen overflow-y-auto ">
      <div className="bg-blue-dark rounded-30 flex flex-col md:flex-row justify-start items-center gap-24 px-24 py-12">
        <div className=" flex-1 max-w-[700px]">
          <h2 className="text-[50px] font-bold text-white mb-4">
            Selamat Datang di CekSertif
          </h2>
          <div className="min-h-[120px] mb-4">
            <h4 className="text-[30px] font-semibold text-white whitespace-pre-line">
              {displayedText}
            </h4>
          </div>
          <Link
            to="/validation"
            className="inline-block bg-white px-5 py-2 rounded-10 font-semibold text-blue-dark text-[20px] shadow-sm hover:bg-blue-light transition-colors duration-300"
          >
            Verifikasi Sekarang
          </Link>
        </div>
        <div className="max-w-[500px] shrink-0 self-start -mt-4">
          <img
            src="/blockchain-ilustrasi-home.png"
            alt="Illustration"
            className="w-full"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <CardStat
          icon={<Icon name="document" className="h-[44px] text-blue-dark" />}
          label="Sertifikat Terbit"
          value={totalTerbit}
        />
        <CardStat
          icon={
            <Icon
              name="document_verified"
              className="h-[44px] text-green-400 "
            />
          }
          label="Sertifikat Terverifikasi"
          value={totalVerified}
          bgColor="bg-green-100 "
        />
        <CardStat
          icon={
            <Icon name="document_alert" className="h-[44px] text-blue-aqua " />
          }
          label="Belum Diverifikasi"
          value={totalBelumVerifikasi}
          bgColor="bg-teal-100"
        />
      </div>

      <div className="mt-6">
        <ActivityTable />
      </div>
    </div>
  );
};

export default Home;
