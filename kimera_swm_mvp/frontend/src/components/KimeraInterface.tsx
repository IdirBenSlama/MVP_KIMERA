import React, { useState } from 'react';
import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

interface Geoid {
  geoid_id: string;
  semantic_state: Record<string, number>;
  symbolic_state: Record<string, any>;
  metadata: Record<string, any>;
}

interface SystemStatus {
  active_geoids: number;
  vault_a_scars: number;
  vault_b_scars: number;
  cycle_count: number;
  system_entropy: number;
}

export default function KimeraInterface() {
  const [geoids, setGeoids] = useState<Geoid[]>([]);
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [contradictionResults, setContradictionResults] = useState<any[]>([]);

  const createGeoid = async (semanticFeatures: Record<string, number>) => {
    const response = await fetch('http://localhost:8000/geoids', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        semantic_features: semanticFeatures,
        metadata: { created_at: new Date().toISOString() }
      })
    });

    const result = await response.json();
    setGeoids(prev => [...prev, result.geoid]);
  };

  const processContradictions = async () => {
    if (geoids.length < 2) return;

    const geoidIds = geoids.slice(0, 2).map(g => g.geoid_id);
    const response = await fetch('http://localhost:8000/process/contradictions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ geoid_ids: geoidIds })
    });

    const results = await response.json();
    setContradictionResults(results.results);
  };

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">KIMERA SWM MVP Interface</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <h2 className="text-xl font-semibold">Create Geoid</h2>
          </CardHeader>
          <CardContent>
            <Button onClick={() => createGeoid({
              'concept_strength': Math.random(),
              'semantic_clarity': Math.random(),
              'contextual_relevance': Math.random()
            })}>
              Create Random Geoid
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <h2 className="text-xl font-semibold">Process Contradictions</h2>
          </CardHeader>
          <CardContent>
            <Button
              onClick={processContradictions}
              disabled={geoids.length < 2}
            >
              Detect Contradictions
            </Button>
          </CardContent>
        </Card>
      </div>

      {contradictionResults.length > 0 && (
        <Card className="mt-6">
          <CardHeader>
            <h2 className="text-xl font-semibold">Contradiction Results</h2>
          </CardHeader>
          <CardContent>
            {contradictionResults.map((result, idx) => (
              <div key={idx} className="mb-4 p-4 border rounded">
                <p><strong>Tension Score:</strong> {result.tension.score.toFixed(3)}</p>
                <p><strong>Pulse Strength:</strong> {result.pulse_strength.toFixed(3)}</p>
                <p><strong>Decision:</strong> {result.decision}</p>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
