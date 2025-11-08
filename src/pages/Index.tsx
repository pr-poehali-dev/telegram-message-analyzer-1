import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import Icon from '@/components/ui/icon';
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
      toast.error('Введите ссылку на сообщение');
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
      
      setWinningPositions(positions);
      
      const result = positions.map(p => 
        `${p.col + 1} столбик ${p.row + 1} квадрат`
      ).join(', ');
      
      setResultText(result);
      toast.success('Анализ завершён!');
      
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
    <div className="min-h-screen bg-gradient-to-br from-background via-purple-950/20 to-background p-4 md:p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        
        <div className="text-center space-y-4 animate-fade-in">
          <div className="inline-block">
            <div className="text-6xl mb-4 animate-bounce-in">🎮</div>
          </div>
          <h1 className="text-5xl md:text-6xl font-bold bg-gradient-to-r from-primary via-secondary to-accent bg-clip-text text-transparent">
            Qalais Analyzer
          </h1>
          <p className="text-lg text-muted-foreground">
            Анализатор игровых уровней Telegram бота
          </p>
        </div>

        <Card className="p-6 md:p-8 bg-card/50 backdrop-blur-sm border-2 border-primary/20 shadow-2xl animate-scale-in">
          <div className="space-y-6">
            <div className="space-y-3">
              <label className="text-sm font-semibold text-foreground flex items-center gap-2">
                <Icon name="Link" size={18} />
                Ссылка на Telegram сообщение
              </label>
              <div className="flex gap-3">
                <Input
                  type="text"
                  placeholder="https://t.me/..."
                  value={telegramUrl}
                  onChange={(e) => setTelegramUrl(e.target.value)}
                  className="flex-1 h-12 bg-input border-border text-foreground placeholder:text-muted-foreground focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all"
                  disabled={isAnalyzing}
                />
                <Button 
                  onClick={analyzeMessage}
                  disabled={isAnalyzing}
                  className="h-12 px-8 bg-gradient-to-r from-primary to-secondary hover:from-primary/90 hover:to-secondary/90 text-primary-foreground font-semibold shadow-lg hover:shadow-primary/50 transition-all duration-300 hover:scale-105"
                >
                  {isAnalyzing ? (
                    <>
                      <Icon name="Loader2" size={20} className="animate-spin mr-2" />
                      Анализирую...
                    </>
                  ) : (
                    <>
                      <Icon name="Sparkles" size={20} className="mr-2" />
                      Анализировать
                    </>
                  )}
                </Button>
              </div>
            </div>

            {isAnalyzing && (
              <div className="flex items-center justify-center py-8 animate-fade-in">
                <div className="text-center space-y-4">
                  <div className="animate-glow-pulse">
                    <Icon name="Zap" size={48} className="text-accent mx-auto" />
                  </div>
                  <p className="text-muted-foreground">Обрабатываю изображение...</p>
                </div>
              </div>
            )}

            {winningPositions.length > 0 && (
              <div className="space-y-6 animate-fade-in">
                <div className="grid grid-cols-3 gap-3 max-w-md mx-auto">
                  {Array.from({ length: 15 }, (_, i) => {
                    const row = Math.floor(i / 3);
                    const col = i % 3;
                    const isWinner = isWinningCell(row, col);
                    
                    return (
                      <button
                        key={i}
                        className={`
                          aspect-square rounded-xl border-2 transition-all duration-300
                          ${isWinner 
                            ? 'bg-gradient-to-br from-accent to-accent/80 border-accent shadow-lg shadow-accent/50 animate-bounce-in scale-105' 
                            : 'bg-muted/30 border-border hover:border-primary/40'
                          }
                        `}
                        style={{
                          animationDelay: isWinner ? `${(row * 3 + col) * 0.1}s` : '0s'
                        }}
                      >
                        {isWinner && (
                          <span className="text-4xl">💸</span>
                        )}
                      </button>
                    );
                  })}
                </div>

                <Card className="p-6 bg-gradient-to-r from-primary/10 to-secondary/10 border-2 border-primary/30 animate-scale-in">
                  <div className="flex items-start gap-4">
                    <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
                      <Icon name="Trophy" size={20} className="text-primary-foreground" />
                    </div>
                    <div className="flex-1">
                      <h3 className="font-bold text-lg mb-2 text-foreground">Правильные позиции:</h3>
                      <p className="text-foreground/90 text-lg">{resultText}</p>
                    </div>
                  </div>
                </Card>
              </div>
            )}
          </div>
        </Card>

        <div className="text-center space-y-3 animate-fade-in opacity-70">
          <p className="text-sm text-muted-foreground flex items-center justify-center gap-2">
            <Icon name="Info" size={16} />
            Вставьте ссылку на сообщение бота с игровым полем
          </p>
        </div>
      </div>
    </div>
  );
}