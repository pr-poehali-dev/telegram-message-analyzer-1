import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { toast } from 'sonner';

interface Position {
  row: number;
  col: number;
}

export default function Index() {
  const [telegramUrl, setTelegramUrl] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [winningPositions, setWinningPositions] = useState<Position[]>([]);
  const [resultText, setResultText] = useState('');

  const analyzeMessage = async () => {
    if (!telegramUrl.trim()) {
      toast.error('Введите ссылку');
      return;
    }

    setIsAnalyzing(true);
    setWinningPositions([]);
    setResultText('');

    try {
      const response = await fetch('https://functions.poehali.dev/e40a9d9a-2d3f-4512-a9ea-cc2ec8933873', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          telegram_url: telegramUrl
        })
      });

      if (!response.ok) {
        throw new Error('Ошибка анализа');
      }

      const data = await response.json();
      const positions: Position[] = data.positions;
      const result = data.result_text || 'Позиции не найдены';
      
      setWinningPositions(positions);
      setResultText(result);
      toast.success('Готово');
      
    } catch (error) {
      toast.error('Ошибка при анализе');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const isWinningCell = (row: number, col: number) => {
    return winningPositions.some(pos => pos.row === row && pos.col === col);
  };

  return (
    <div className="min-h-screen bg-background p-4 md:p-8 flex items-center justify-center">
      <div className="w-full max-w-2xl space-y-8">
        
        <div className="space-y-2">
          <h1 className="text-3xl font-semibold text-foreground tracking-tight">
            Qalais Analyzer
          </h1>
          <p className="text-sm text-muted-foreground">
            Анализ игрового поля
          </p>
        </div>

        <div className="space-y-6">
          <div className="space-y-2">
            <label className="text-sm font-medium text-foreground">
              Ссылка на сообщение или изображение
            </label>
            <div className="flex gap-2">
              <Input
                type="text"
                placeholder="https://..."
                value={telegramUrl}
                onChange={(e) => setTelegramUrl(e.target.value)}
                className="h-10 border-border"
                disabled={isAnalyzing}
              />
              <Button 
                onClick={analyzeMessage}
                disabled={isAnalyzing}
                className="h-10 px-6"
              >
                {isAnalyzing ? 'Анализ...' : 'Анализировать'}
              </Button>
            </div>
          </div>

          {isAnalyzing && (
            <div className="flex items-center justify-center py-12">
              <div className="text-sm text-muted-foreground">
                Обработка изображения...
              </div>
            </div>
          )}

          {winningPositions.length > 0 && (
            <div className="space-y-4">
              <div className="grid grid-cols-3 gap-2 max-w-sm mx-auto">
                {Array.from({ length: 15 }, (_, i) => {
                  const row = Math.floor(i / 3);
                  const col = i % 3;
                  const isWinner = isWinningCell(row, col);
                  
                  return (
                    <div
                      key={i}
                      className={`
                        aspect-square rounded border flex items-center justify-center text-2xl
                        ${isWinner 
                          ? 'bg-accent text-accent-foreground border-accent' 
                          : 'bg-secondary border-border'
                        }
                      `}
                    >
                      {isWinner && '💸'}
                    </div>
                  );
                })}
              </div>

              <div className="p-4 border border-border rounded bg-card">
                <div className="text-sm font-medium text-foreground mb-1">
                  Правильные позиции:
                </div>
                <div className="text-sm text-foreground">
                  {resultText}
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="text-xs text-muted-foreground text-center">
          Вставьте ссылку на Telegram сообщение или прямую ссылку на изображение
        </div>
      </div>
    </div>
  );
}