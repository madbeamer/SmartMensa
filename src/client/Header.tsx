import "./Header.css";
import { ImFilter } from "react-icons/im";
import { FaGear } from "react-icons/fa6";
import { useLocation, useNavigate } from "react-router-dom";
import { MdArrowBackIos } from "react-icons/md";

interface HeaderProps {
  onFilterClick: () => void;
  onSettingsClick: () => void;
}

function Header({ onFilterClick, onSettingsClick }: HeaderProps) {
  const navigate = useNavigate();

  const handleBackClick = () => {
    navigate("/home");
  };

  const location = useLocation();
  const isHomeRoute = location.pathname === "/home";

  return (
    <>
      <header>
        {isHomeRoute ? (
          <div id="filter-button">
            <ImFilter size={30} onClick={onFilterClick} />
          </div>
        ) : (
          <div id="back-button">
            <MdArrowBackIos size={30} onClick={() => handleBackClick()} />
          </div>
        )}
        <div id="app-name">
          <span>SmartMensa</span>
        </div>
        <div id="settings-button">
          <FaGear size={30} onClick={onSettingsClick} />
        </div>
      </header>
    </>
  );
}

export default Header;
