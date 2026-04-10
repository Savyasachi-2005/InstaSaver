import { Route, Routes } from "react-router-dom";

import ShellLayout from "./components/ShellLayout";
import HomePage from "./pages/HomePage";
import PostPage from "./pages/PostPage";
import ReelPage from "./pages/ReelPage";

function App() {
  return (
    <ShellLayout>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/reels" element={<ReelPage />} />
        <Route path="/posts" element={<PostPage />} />
      </Routes>
    </ShellLayout>
  );
}

export default App;
