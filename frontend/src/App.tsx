import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Layout } from './components/Layout';
import { ChatView } from './views/ChatView';
import { WorkflowView } from './views/WorkflowView';
import { SettingsView } from './views/SettingsView';

export function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<ChatView />} />
          <Route path="/workflows" element={<WorkflowView />} />
          <Route path="/settings" element={<SettingsView />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}
