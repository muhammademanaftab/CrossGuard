"""Integration tests with real-world HTML samples.

Tests: Complete web pages, common website patterns
"""

import pytest


class TestModernWebPage:
    """Tests for modern web page patterns."""

    def test_landing_page(self, parse_html):
        """Test modern landing page structure."""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta name="theme-color" content="#4285f4">
            <link rel="icon" type="image/svg+xml" href="favicon.svg">
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link rel="preload" href="hero.jpg" as="image">
            <title>Landing Page</title>
        </head>
        <body>
            <header>
                <nav aria-label="Main navigation">
                    <a href="/" aria-current="page">Home</a>
                    <a href="/about">About</a>
                    <a href="/contact">Contact</a>
                </nav>
            </header>

            <main>
                <section class="hero">
                    <h1>Welcome</h1>
                    <picture>
                        <source srcset="hero.avif" type="image/avif">
                        <source srcset="hero.webp" type="image/webp">
                        <img src="hero.jpg" alt="Hero image" loading="eager">
                    </picture>
                </section>

                <section class="features">
                    <article>
                        <figure>
                            <img src="feature1.jpg" loading="lazy" alt="Feature 1">
                            <figcaption>Feature 1 description</figcaption>
                        </figure>
                    </article>
                </section>

                <section class="video-section">
                    <video poster="poster.jpg" controls>
                        <source src="intro.webm" type="video/webm">
                        <source src="intro.mp4" type="video/mp4">
                        <track kind="captions" src="captions.vtt" srclang="en" label="English">
                    </video>
                </section>
            </main>

            <footer>
                <nav aria-label="Footer navigation">
                    <a href="/privacy" rel="noopener">Privacy</a>
                    <a href="/terms" rel="noopener">Terms</a>
                </nav>
                <p>&copy; 2024</p>
            </footer>
        </body>
        </html>
        """
        features = parse_html(html)

        # Meta features
        assert 'viewport-units' in features
        assert 'meta-theme-color' in features
        assert 'link-icon-svg' in features
        assert 'link-rel-preconnect' in features
        assert 'link-rel-preload' in features

        # Semantic features
        assert 'html5semantic' in features
        assert 'wai-aria' in features

        # Media features
        assert 'picture' in features
        assert 'avif' in features
        assert 'webp' in features
        assert 'loading-lazy-attr' in features
        assert 'video' in features
        assert 'webm' in features
        assert 'webvtt' in features

        # Link features
        assert 'rel-noopener' in features

    def test_blog_post_page(self, parse_html):
        """Test blog post page structure."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width">
        </head>
        <body>
            <header>
                <nav>
                    <a href="/">Blog</a>
                </nav>
            </header>

            <main>
                <article>
                    <header>
                        <h1>Blog Post Title</h1>
                        <time datetime="2024-01-15">January 15, 2024</time>
                        <p>By <span translate="no">John Doe</span></p>
                    </header>

                    <section>
                        <p>Article content with <mark>highlighted text</mark>.</p>

                        <figure>
                            <img src="article-image.jpg"
                                 srcset="article-image-400.jpg 400w,
                                         article-image-800.jpg 800w"
                                 sizes="(max-width: 800px) 100vw, 800px"
                                 loading="lazy"
                                 alt="Article illustration">
                            <figcaption>Figure 1: Illustration</figcaption>
                        </figure>

                        <pre><code translate="no">console.log('Hello');</code></pre>
                    </section>

                    <footer>
                        <p>Tags: <a href="/tag/web">Web</a></p>
                    </footer>
                </article>

                <aside aria-label="Related posts">
                    <h2>Related Posts</h2>
                    <ul>
                        <li><a href="/post/1">Related Post 1</a></li>
                    </ul>
                </aside>
            </main>

            <section id="comments">
                <h2>Comments</h2>
                <form>
                    <label>
                        Name:
                        <input type="text" required autocomplete="name">
                    </label>
                    <label>
                        Email:
                        <input type="email" required autocomplete="email">
                    </label>
                    <label>
                        Comment:
                        <textarea required minlength="10" maxlength="1000"></textarea>
                    </label>
                    <button type="submit">Post Comment</button>
                </form>
            </section>
        </body>
        </html>
        """
        features = parse_html(html)

        assert 'html5semantic' in features
        assert 'srcset' in features
        assert 'loading-lazy-attr' in features
        assert 'internationalization' in features  # translate
        assert 'form-validation' in features
        assert 'input-autocomplete-onoff' in features
        assert 'input-minlength' in features
        assert 'maxlength' in features
        assert 'wai-aria' in features


class TestWebApplication:
    """Tests for web application patterns."""

    def test_spa_shell(self, parse_html):
        """Test SPA shell structure."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta http-equiv="content-security-policy"
                  content="default-src 'self'; script-src 'self'">
            <link rel="modulepreload" href="vendor.js">
            <link rel="modulepreload" href="app.js">
            <script type="module" src="app.js" defer></script>
        </head>
        <body onhashchange="router()">
            <div id="app">
                <my-app-shell>
                    <nav slot="navigation" aria-label="Main">
                        <a href="#/" aria-current="page">Home</a>
                        <a href="#/about">About</a>
                    </nav>
                    <main slot="content" aria-live="polite">
                        Loading...
                    </main>
                </my-app-shell>
            </div>

            <template id="page-template">
                <article>
                    <slot name="title"></slot>
                    <slot name="content"></slot>
                </article>
            </template>

            <dialog id="modal" aria-modal="true">
                <form method="dialog">
                    <slot name="dialog-content"></slot>
                    <button type="submit">Close</button>
                </form>
            </dialog>
        </body>
        </html>
        """
        features = parse_html(html)

        assert 'contentsecuritypolicy2' in features
        assert 'link-rel-modulepreload' in features
        assert 'es6-module' in features
        assert 'script-defer' in features
        assert 'hashchange' in features
        assert 'custom-elementsv1' in features
        assert 'shadowdomv1' in features  # slot
        assert 'template' in features
        assert 'dialog' in features
        assert 'wai-aria' in features

    def test_dashboard_page(self, parse_html):
        """Test dashboard page with charts and data."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width">
        </head>
        <body>
            <main>
                <h1>Dashboard</h1>

                <section aria-labelledby="metrics-title">
                    <h2 id="metrics-title">Metrics</h2>

                    <div class="metric">
                        <p>CPU Usage</p>
                        <meter min="0" max="100" value="45" low="25" high="75">45%</meter>
                    </div>

                    <div class="metric">
                        <p>Memory</p>
                        <meter min="0" max="100" value="72">72%</meter>
                    </div>

                    <div class="metric">
                        <p>Task Progress</p>
                        <progress value="30" max="100">30%</progress>
                    </div>
                </section>

                <section aria-labelledby="chart-title">
                    <h2 id="chart-title">Charts</h2>
                    <canvas id="sales-chart" width="800" height="400"
                            aria-label="Sales chart" role="img">
                    </canvas>

                    <svg viewBox="0 0 400 200" aria-label="Pie chart" role="img">
                        <circle cx="100" cy="100" r="80" fill="blue"/>
                    </svg>
                </section>

                <section aria-labelledby="data-title">
                    <h2 id="data-title">Data Table</h2>
                    <table>
                        <thead>
                            <tr>
                                <th aria-sort="ascending">Name</th>
                                <th>Value</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr><td>Item 1</td><td>100</td></tr>
                        </tbody>
                    </table>
                </section>
            </main>
        </body>
        </html>
        """
        features = parse_html(html)

        assert 'meter' in features
        assert 'progress' in features
        assert 'canvas' in features
        assert 'svg' in features
        assert 'wai-aria' in features


class TestEcommercePages:
    """Tests for e-commerce page patterns."""

    def test_product_page(self, parse_html):
        """Test product page structure."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width">
        </head>
        <body>
            <main>
                <article itemscope itemtype="https://schema.org/Product">
                    <h1 itemprop="name">Product Name</h1>

                    <section aria-label="Product images">
                        <picture>
                            <source srcset="product.avif" type="image/avif">
                            <source srcset="product.webp" type="image/webp">
                            <img src="product.jpg" alt="Product" loading="eager">
                        </picture>
                    </section>

                    <section aria-label="Product details">
                        <p>Price: $99.99</p>
                        <p>Rating: <meter min="0" max="5" value="4.5">4.5 out of 5</meter></p>
                    </section>

                    <form>
                        <fieldset>
                            <legend>Options</legend>

                            <label>
                                Color:
                                <input type="color" name="color" value="#000000">
                            </label>

                            <label>
                                Size:
                                <input list="sizes" name="size" required>
                                <datalist id="sizes">
                                    <option value="S">
                                    <option value="M">
                                    <option value="L">
                                </datalist>
                            </label>

                            <label>
                                Quantity:
                                <input type="number" name="quantity" min="1" max="10" value="1">
                            </label>
                        </fieldset>

                        <button type="submit">Add to Cart</button>
                    </form>
                </article>

                <section aria-label="Product video">
                    <video poster="video-poster.jpg" controls>
                        <source src="product-video.webm" type="video/webm">
                        <source src="product-video.mp4" type="video/mp4">
                    </video>
                </section>
            </main>
        </body>
        </html>
        """
        features = parse_html(html)

        assert 'picture' in features
        assert 'avif' in features
        assert 'webp' in features
        assert 'meter' in features
        assert 'input-color' in features
        assert 'datalist' in features
        assert 'input-number' in features
        assert 'form-validation' in features
        assert 'video' in features
        assert 'wai-aria' in features

    def test_checkout_form(self, parse_html):
        """Test checkout form structure."""
        html = """
        <form id="checkout">
            <fieldset>
                <legend>Contact Information</legend>
                <label>
                    Email:
                    <input type="email" name="email" required autocomplete="email"
                           inputmode="email" placeholder="you@example.com">
                </label>
                <label>
                    Phone:
                    <input type="tel" name="phone" autocomplete="tel"
                           inputmode="tel" pattern="[0-9]{10}">
                </label>
            </fieldset>

            <fieldset>
                <legend>Shipping Address</legend>
                <label>
                    Street:
                    <input type="text" name="street" required autocomplete="street-address">
                </label>
                <label>
                    City:
                    <input type="text" name="city" required autocomplete="address-level2">
                </label>
                <label>
                    ZIP:
                    <input type="text" name="zip" required autocomplete="postal-code"
                           inputmode="numeric" pattern="[0-9]{5}">
                </label>
            </fieldset>

            <fieldset>
                <legend>Payment</legend>
                <label>
                    Card Number:
                    <input type="text" name="card" required autocomplete="cc-number"
                           inputmode="numeric" minlength="16" maxlength="16">
                </label>
                <label>
                    Expiry:
                    <input type="month" name="expiry" required autocomplete="cc-exp">
                </label>
            </fieldset>

            <button type="submit">Place Order</button>
        </form>
        """
        features = parse_html(html)

        assert 'input-email-tel-url' in features
        assert 'form-validation' in features
        assert 'input-autocomplete-onoff' in features
        assert 'input-inputmode' in features
        assert 'input-pattern' in features
        assert 'input-placeholder' in features
        assert 'input-minlength' in features
        assert 'maxlength' in features
        assert 'input-datetime' in features  # month


class TestAccessiblePages:
    """Tests for accessible web page patterns."""

    def test_fully_accessible_page(self, parse_html):
        """Test fully accessible page structure."""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width">
        </head>
        <body>
            <a href="#main-content" class="skip-link">Skip to main content</a>

            <header role="banner">
                <nav role="navigation" aria-label="Main navigation">
                    <ul role="menubar">
                        <li role="none">
                            <a href="/" role="menuitem" aria-current="page">Home</a>
                        </li>
                        <li role="none">
                            <button role="menuitem" aria-haspopup="true" aria-expanded="false">
                                Products
                            </button>
                            <ul role="menu" aria-label="Products submenu" hidden>
                                <li role="none"><a href="/p1" role="menuitem">Product 1</a></li>
                            </ul>
                        </li>
                    </ul>
                </nav>

                <form role="search" aria-label="Site search">
                    <label for="search">Search:</label>
                    <input type="search" id="search" name="q"
                           aria-describedby="search-hint">
                    <span id="search-hint" class="sr-only">
                        Enter keywords to search
                    </span>
                    <button type="submit" aria-label="Submit search">
                        <svg aria-hidden="true"><use href="#icon-search"></use></svg>
                    </button>
                </form>
            </header>

            <main id="main-content" role="main" aria-labelledby="page-title">
                <h1 id="page-title">Page Title</h1>

                <section aria-labelledby="section-1">
                    <h2 id="section-1">Section 1</h2>

                    <div role="tablist" aria-label="Content tabs">
                        <button role="tab" aria-selected="true" aria-controls="panel-1"
                                id="tab-1">Tab 1</button>
                        <button role="tab" aria-selected="false" aria-controls="panel-2"
                                id="tab-2">Tab 2</button>
                    </div>

                    <div role="tabpanel" id="panel-1" aria-labelledby="tab-1">
                        Panel 1 content
                    </div>
                    <div role="tabpanel" id="panel-2" aria-labelledby="tab-2" hidden>
                        Panel 2 content
                    </div>
                </section>

                <section aria-labelledby="section-2">
                    <h2 id="section-2">Alerts</h2>

                    <div role="alert" aria-live="assertive">
                        Important message
                    </div>

                    <div role="status" aria-live="polite" aria-atomic="true">
                        Status update
                    </div>
                </section>
            </main>

            <aside role="complementary" aria-labelledby="sidebar-title">
                <h2 id="sidebar-title">Sidebar</h2>
            </aside>

            <footer role="contentinfo">
                <p>&copy; 2024</p>
            </footer>
        </body>
        </html>
        """
        features = parse_html(html)

        assert 'wai-aria' in features
        assert 'html5semantic' in features
        assert 'input-search' in features
        assert 'hidden' in features
        assert 'svg-fragment' in features


class TestMediaRichPages:
    """Tests for media-rich page patterns."""

    def test_video_gallery(self, parse_html):
        """Test video gallery page."""
        html = """
        <main>
            <h1>Video Gallery</h1>

            <section aria-label="Featured video">
                <video id="player"
                       poster="featured-poster.jpg"
                       controls
                       crossorigin="anonymous">
                    <source src="featured.webm" type="video/webm">
                    <source src="featured.mp4" type="video/mp4">
                    <track kind="captions" src="featured-en.vtt" srclang="en" label="English" default>
                    <track kind="captions" src="featured-es.vtt" srclang="es" label="Spanish">
                    <track kind="descriptions" src="featured-desc.vtt" srclang="en">
                    <track kind="chapters" src="featured-chapters.vtt" srclang="en">
                </video>
            </section>

            <section aria-label="Video thumbnails">
                <ul>
                    <li>
                        <a href="#" data-video="video1.mp4">
                            <img src="thumb1.jpg" srcset="thumb1.jpg 1x, thumb1@2x.jpg 2x"
                                 loading="lazy" alt="Video 1">
                        </a>
                    </li>
                    <li>
                        <a href="#" data-video="video2.mp4">
                            <img src="thumb2.jpg" srcset="thumb2.jpg 1x, thumb2@2x.jpg 2x"
                                 loading="lazy" alt="Video 2">
                        </a>
                    </li>
                </ul>
            </section>

            <section aria-label="Audio playlist">
                <audio controls>
                    <source src="audio.opus" type="audio/opus">
                    <source src="audio.mp3" type="audio/mpeg">
                    <track kind="captions" src="audio-transcript.vtt">
                </audio>
            </section>
        </main>
        """
        features = parse_html(html)

        assert 'video' in features
        assert 'cors' in features
        assert 'webm' in features
        assert 'mpeg4' in features
        assert 'webvtt' in features
        assert 'videotracks' in features
        assert 'srcset' in features
        assert 'loading-lazy-attr' in features
        assert 'dataset' in features
        assert 'audio' in features
        assert 'opus' in features
        assert 'mp3' in features
        assert 'audiotracks' in features
