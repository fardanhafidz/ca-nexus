/** @type {import('next').NextConfig} */
const nextConfig = {
  // DEL-I2: minimal production image (requires `output: standalone` tracing)
  output: "standalone",
};
module.exports = nextConfig;
