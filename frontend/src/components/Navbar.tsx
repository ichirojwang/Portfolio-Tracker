import ButtonLink from "./ButtonLink";
import ButtonLogout from "./ButtonLogout";
import LogoSmall from "./LogoSmall";

const Navbar = () => {
  return (
    <nav className="mx-3 my-5 flex items-center gap-2">
      <LogoSmall className="mr-2" />
      <ButtonLink to="/home">Home</ButtonLink>
      <ButtonLink to="/portfolios">Portfolios</ButtonLink>
      <ButtonLink to="/settings">Settings</ButtonLink>
      <ButtonLogout />
    </nav>
  );
};

export default Navbar;
