import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './components/Dashboard';
import PhenotypeComparison from './components/PhenotypeComparison';
import MeetingList from './components/MeetingList';
import MeetingDetail from './components/MeetingDetail';
import AudioUpload from './components/AudioUpload';
import ReportViewer from './components/ReportViewer';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="phenotype" element={<PhenotypeComparison />} />
        <Route path="meetings" element={<MeetingList />} />
        <Route path="meetings/:id" element={<MeetingDetail />} />
        <Route path="upload" element={<AudioUpload />} />
        <Route path="reports/:id" element={<ReportViewer />} />
      </Route>
    </Routes>
  );
}

export default App;
