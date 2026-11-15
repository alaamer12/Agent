# Polyglot Calibration Walkthrough & Comparative Patterns

Demonstrates how to apply North Star design calibration across diverse frontend platforms without monoculture bias.

> **Standing Note**: All language choices below (React/TypeScript, Flutter/Dart, SwiftUI/Swift, Vue/Svelte) are illustrative reference implementations. The calibration principles apply universally to any declarative or imperative UI stack.

---

## Pattern 1: Card Architecture with Micro-Sparkline & Pastel Badge

### Target State Requirements:
- Strict boundary containment `[overflow: hidden / clipBehavior: antiAlias]`.
- Pinned circular pastel icon badge `[e.g. 44x44px]`.
- Embedded micro-visualization / sparkline anchored at the base.
- Tabular / monospace figure display with clear hierarchy.

---

### React & Tailwind (TypeScript)

```tsx
interface MetricCardProps {
  title: string;
  value: string;
  trend: string;
  points: number[];
  colorPair: { badgeBg: string; badgeText: string; stroke: string };
  iconSvg: React.ReactNode;
}

export function MetricCard({ title, value, trend, points, colorPair, iconSvg }: MetricCardProps) {
  return (
    <div className="relative overflow-hidden bg-white rounded-2xl p-5 border border-slate-200/80 shadow-sm hover:shadow-md transition-shadow min-h-[145px] flex flex-col justify-between">
      {/* Pinned Icon Badge */}
      <div className={`absolute top-5 left-5 w-11 h-11 rounded-full ${colorPair.badgeBg} ${colorPair.badgeText} flex items-center justify-center shrink-0 shadow-sm z-10`}>
        {iconSvg}
      </div>

      {/* Contained Micro-Sparkline */}
      <div className="absolute bottom-1 left-2 w-28 h-9 pointer-events-none z-0 overflow-hidden">
        <SparklineRenderer points={points} color={colorPair.stroke} />
      </div>

      {/* Metrics Stack */}
      <div className="relative z-10 pr-0 pl-16 text-right">
        <span className="text-sm font-bold text-slate-700">{title}</span>
        <div className="text-3xl font-black font-mono text-slate-900 my-2">{value}</div>
        <span className="text-xs font-bold text-emerald-600">{trend}</span>
      </div>
    </div>
  );
}
```

---

### Flutter (Dart)

```dart
class MetricCard extends StatelessWidget {
  final String title;
  final String value;
  final String trend;
  final Color badgeBg;
  final Color badgeColor;
  final Widget icon;
  final List<double> sparklinePoints;

  const MetricCard({
    super.key,
    required this.title,
    required this.value,
    required this.trend,
    required this.badgeBg,
    required this.badgeColor,
    required this.icon,
    required this.sparklinePoints,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      clipBehavior: Clip.antiAlias, // Strict containment
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFE2E8F0)),
        boxShadow: const [
          BoxShadow(color: Color(0x0A000000), blurRadius: 4, offset: Offset(0, 1)),
        ],
      ),
      child: Stack(
        children: [
          // Pinned Badge
          Positioned(
            top: 20,
            left: 20,
            child: Container(
              width: 44,
              height: 44,
              decoration: BoxDecoration(
                color: badgeBg,
                shape: BoxShape.circle,
              ),
              child: Center(child: icon),
            ),
          ),
          // Bounded Micro-Sparkline
          Positioned(
            bottom: 4,
            left: 8,
            width: 112,
            height: 36,
            child: CustomPaint(
              painter: SparklinePainter(points: sparklinePoints, color: badgeColor),
            ),
          ),
          // Content Stack
          Padding(
            padding: const EdgeInsets.only(top: 20, right: 20, bottom: 20, left: 74),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                const SizedBox(height: 8),
                Text(value, style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 28, fontFamily: 'monospace')),
                const SizedBox(height: 6),
                Text(trend, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12, color: Color(0xFF10B981))),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
```

---

### SwiftUI (Swift)

```swift
struct MetricCardView: View {
    let title: String
    let value: String
    let trend: String
    let badgeBg: Color
    let badgeColor: Color
    let systemIcon: String
    let points: [Double]

    var body: some View {
        ZStack {
            // Contained Sparkline at Bottom
            VStack {
                Spacer()
                HStack {
                    SparklineShape(points: points)
                        .stroke(badgeColor, lineWidth: 2)
                        .frame(width: 112, height: 36)
                    Spacer()
                }
                .padding(.leading, 8)
                .padding(.bottom, 4)
            }

            // Main Content Stack
            HStack(alignment: .top) {
                // Circular Badge
                ZStack {
                    Circle()
                        .fill(badgeBg)
                        .frame(width: 44, height: 44)
                    Image(systemName: systemIcon)
                        .foregroundColor(badgeColor)
                }

                Spacer()

                VStack(alignment: .trailing, spacing: 6) {
                    Text(title)
                        .font(.system(size: 14, weight: .bold))
                        .foregroundColor(.secondary)
                    Text(value)
                        .font(.system(size: 28, weight: .black, design: .monospaced))
                        .foregroundColor(.primary)
                    Text(trend)
                        .font(.system(size: 12, weight: .bold))
                        .foregroundColor(.green)
                }
            }
            .padding(20)
        }
        .background(Color.white)
        .cornerRadius(16)
        .overlay(
            RoundedRectangle(cornerRadius: 16)
                .stroke(Color(.systemGray5), lineWidth: 1)
        )
        .clipped() // Strict boundary containment
        .shadow(color: Color.black.opacity(0.04), radius: 3, x: 0, y: 1)
    }
}
```

---

## Pattern 2: Ambient Atmosphere Layering

```html
<!-- Ambient canvas background: out-of-flow, non-interactive, isolated IDs -->
<div class="absolute -top-10 right-0 left-0 h-96 pointer-events-none overflow-hidden -z-10">
  <div class="absolute top-0 right-1/4 w-[600px] h-72 bg-emerald-100/40 rounded-full blur-3xl"></div>
  <div class="absolute top-10 left-10 w-80 h-80 bg-teal-50/70 rounded-full blur-2xl"></div>
  
  <!-- Unique Pattern ID per View to Prevent Collisions -->
  <svg class="absolute top-6 left-12 w-36 h-24 opacity-30 text-teal-600" fill="currentColor">
    <pattern id="dotMatrix_Instance" x="0" y="0" width="16" height="16" patternUnits="userSpaceOnUse">
      <circle cx="3" cy="3" r="1.8" />
    </pattern>
    <rect width="100%" height="100%" fill="url(#dotMatrix_Instance)" />
  </svg>
</div>
```

---

## Pattern 3: Deterministic Data Simulation Contract

```typescript
// Shared contract across all views:
// When simulation flag is active -> deterministic PRNG generated metrics
// When absent -> clean honest baseline state (zeros / empty placeholders)

export function resolveSimulationState<T>(
  flagValue: string | null,
  generator: (rng: () => number) => T,
  fallback: T
): T {
  if (!flagValue) return fallback;
  
  const seed = flagValue === 'true' || flagValue === '1' ? 42 : hashStringToNumber(flagValue);
  const prng = createMulberry32(seed);
  return generator(prng);
}
```
