import React, { useState } from 'react';
import './App.css';
import TeamSearch from './components/TeamSearch';
import TeamAnalysis from './components/TeamAnalysis';

interface TeamData {
  team_id: number;
  team_name: string;
  manager_name: string;
  current_rank: number;
  total_points: number;
  current_gameweek: number;
  transfers_remaining: number;
  transfer_bank: number;
}

const App: React.FC = () => {
  const [teamData, setTeamData] = useState<TeamData | null>(null);
  const [loading, setLoading] = useState(false);

  const handleTeamSelect = async (teamId: number) => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:5000/api/team/${teamId}/summary`);
      if (!response.ok) throw new Error('Failed to fetch team');
      const data = await response.json();
      setTeamData(data);
    } catch (error) {
      console.error('Error fetching team:', error);
      alert('Failed to fetch team data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>FPL Assistant</h1>
        <p>Fantasy Premier League Transfer Recommendations</p>
      </header>

      <main className="App-main">
        <TeamSearch onTeamSelect={handleTeamSelect} loading={loading} />
        {teamData && <TeamAnalysis teamData={teamData} />}
      </main>
    </div>
  );
};

export default App;
