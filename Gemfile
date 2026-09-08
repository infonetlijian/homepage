source "https://rubygems.org"

# GitHub Pages 经典构建（Deploy from a branch）官方推荐配置：
# 使用 github-pages gem，版本与 Pages 构建环境一致（含 jekyll 3.10 + kramdown + Primer 主题等白名单依赖）
gem "github-pages", group: :jekyll_plugins

# Windows does not include zoneinfo files, so bundle the tzinfo-data gem (本地预览用)
gem "tzinfo-data", platforms: [:mingw, :mswin, :x64_mingw, :jruby]

# Performance-booster for watching directories on Windows (本地预览用)
gem "wdm", "~> 0.2.0" if Gem.win_platform?

# Ruby 3+ 本地 `bundle exec jekyll serve` 需要 (Pages 环境自带,无需安装)
gem "webrick", "~> 1.7"
